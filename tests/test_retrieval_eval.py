"""Retrieval-eval helpers for the embedding comparison (docs/experiments.md v12)."""

import pytest
from sqlalchemy import text

from app.models.chunk import Chunk
from app.models.document import Document
from app.services.chunking import build_embedding_text
from eval import retrieval_runs
from eval.retrieval_checks import (
    VectorModelMismatch,
    check_stored_vectors,
    dense_search_plan,
    force_exact_search,
)
from eval.run_retrieval_eval import hit_at_k, reciprocal_rank
from tests.conftest import EMBEDDING_DIM, FakeEmbeddingService


def test_hits_count_the_other_translation_of_an_expected_page():
    expected = ["docs/ko/docs/tutorial/body.md"]
    ranked = ["docs/en/docs/tutorial/cors.md", "docs/en/docs/tutorial/body.md"]

    assert hit_at_k(ranked, expected, 2)
    assert not hit_at_k(ranked, expected, 1)
    assert reciprocal_rank(ranked, expected) == 0.5


def test_single_language_results_score_exactly_as_before():
    expected = ["docs/ko/docs/a.md", "docs/ko/docs/b.md"]
    ranked = ["docs/ko/docs/c.md", "docs/ko/docs/b.md", "docs/ko/docs/a.md"]

    assert reciprocal_rank(ranked, expected) == 0.5
    assert hit_at_k(ranked, expected, 2) and not hit_at_k(ranked, expected, 1)
    assert reciprocal_rank(["docs/ko/docs/z.md"], expected) == 0.0


@pytest.mark.asyncio
async def test_exact_search_turns_off_index_scans_for_the_session(db_session):
    await force_exact_search(db_session)

    assert (await db_session.execute(text("SHOW enable_indexscan"))).scalar() == "off"


class OtherEmbeddingService(FakeEmbeddingService):
    """A different model: same interface, unrelated vectors."""

    def __init__(self) -> None:
        self.model_name = "other-embedding"

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (EMBEDDING_DIM - 1) for _ in texts]


async def _seed_embedded_chunk(db_session, embedder, language: str = "ko") -> None:
    document = Document(
        source_path=f"docs/{language}/docs/a.md", title="A", source_commit_sha="x", content_hash="h"
    )
    db_session.add(document)
    await db_session.flush()
    heading, content = "A > B", "경로 매개변수는 경로 문자열에 선언합니다."
    db_session.add(
        Chunk(
            document_id=document.id,
            chunk_index=0,
            heading_path=heading,
            content=content,
            token_count=10,
            embedding=embedder.embed_passages([build_embedding_text(heading, content)])[0],
            language=language,
        )
    )
    await db_session.commit()


@pytest.mark.asyncio
async def test_vector_check_passes_for_the_model_that_embedded_the_chunks(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    checked = await check_stored_vectors(db_session, FakeEmbeddingService(), "ko")

    assert checked["checked"] == 1
    assert checked["min_cosine"] > 0.999


@pytest.mark.asyncio
async def test_vector_check_refuses_a_database_embedded_by_another_model(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    with pytest.raises(VectorModelMismatch):
        await check_stored_vectors(db_session, OtherEmbeddingService(), "ko")


@pytest.mark.asyncio
async def test_vector_check_refuses_a_language_with_no_chunks(db_session):
    with pytest.raises(VectorModelMismatch):
        await check_stored_vectors(db_session, FakeEmbeddingService(), "en")


def _record(qid: str, scores: list[float], hit_rank: int | None, dataset: str = "d") -> dict:
    paths = [f"docs/ko/docs/p{i}.md" for i in range(len(scores))]
    expected = [paths[hit_rank - 1]] if hit_rank else ["docs/ko/docs/missing.md"]
    return {
        "id": qid,
        "dataset": dataset,
        "expected_source_paths": expected,
        "results": [
            {"rank": i + 1, "chunk_id": f"{qid}-{i}", "source_path": p, "score": s}
            for i, (p, s) in enumerate(zip(paths, scores, strict=True))
        ],
    }


def test_metrics_at_a_floor_drop_results_under_it():
    records = [
        _record("q1", [0.9, 0.8, 0.7, 0.6, 0.5, 0.4], hit_rank=2),
        _record("q2", [0.5, 0.4, 0.29, 0.28, 0.27], hit_rank=3),
    ]

    at_zero = retrieval_runs.metrics(records, floor=0.0)
    at_shared = retrieval_runs.metrics(records, floor=0.3)

    assert at_zero["mrr"] == pytest.approx((1 / 2 + 1 / 3) / 2)
    assert at_zero["short"] == 0
    assert at_shared["mrr"] == pytest.approx((1 / 2 + 0) / 2)  # q2's hit fell under 0.3
    assert at_shared["short"] == 1  # q2 keeps 2 results, fewer than 5


def test_floor_rule_keeps_the_shared_floor_when_every_question_keeps_five():
    records = [_record("q1", [0.9, 0.8, 0.7, 0.6, 0.31, 0.2], hit_rank=1)]

    assert retrieval_runs.pick_floor(records) == 0.3


def test_floor_rule_lowers_the_floor_until_every_question_keeps_five():
    records = [
        _record("q1", [0.9, 0.8, 0.7, 0.6, 0.5], hit_rank=1),
        _record("q2", [0.4, 0.3, 0.26, 0.22, 0.21, 0.1], hit_rank=1),
    ]

    # q2's fifth score is 0.21: 0.25 would cut it to 3 results, 0.2 keeps 5.
    assert retrieval_runs.pick_floor(records) == 0.2


def test_comparing_two_runs_reports_questions_whose_ranking_changed():
    a = [_record("q1", [0.9, 0.8], hit_rank=1), _record("q2", [0.9, 0.8], hit_rank=2)]
    b = [_record("q1", [0.9, 0.8], hit_rank=1), _record("q2", [0.9, 0.85], hit_rank=1)]
    b[1]["results"][0]["chunk_id"] = "moved"

    diff = retrieval_runs.compare(a, b, top=10)

    assert diff["same_ranking"] == 1
    assert diff["changed_ids"] == ["q2"]
    assert diff["mrr_a"] == pytest.approx(0.75) and diff["mrr_b"] == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_dense_plan_names_the_scan_and_exact_search_avoids_the_index(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    await force_exact_search(db_session)
    nodes = await dense_search_plan(db_session, "ko")

    assert any(node.startswith("Seq Scan on chunks") for node in nodes)
    assert not any("hnsw" in node for node in nodes)
    assert await dense_search_plan(db_session, "en") == []  # no English chunks to plan with
