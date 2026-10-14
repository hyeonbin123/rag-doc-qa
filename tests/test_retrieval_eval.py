"""임베딩 비교(docs/experiments.md v12)를 위한 검색 평가 도우미들을 검증한다."""

# [테스트 묶음] v12 한국어 임베딩 비교를 위해 넓힌 검색 평가 하네스의 테스트: 페이지 단위
# Hit·MRR(eval/run_retrieval_eval.py), 측정 전 확인(eval/retrieval_checks.py의 정확 탐색 전환·저장 벡터
# 확인·실행 계획), 기록 분석(eval/retrieval_runs.py의 바닥값 규칙·두 실행 비교).
# [왜 중요한가] 이 도구들의 숫자로 한국어 임베딩 교체를 결정했다(docs/experiments.md v12, v13 단계 B). Hit
# 정의가 이전과 달라지거나, 다른 모델의 DB를 그대로 재거나, 바닥값 규칙이 틀리면 결정이 틀어진다.
# [import] SQLAlchemy text는 세션 설정(SHOW enable_indexscan)을 직접 읽는 데 쓴다.

import pytest
from sqlalchemy import text

# 테스트 데이터로 넣을 문서·청크 모델과 적재와 같은 임베딩 입력 함수, 테스트 대상 평가 모듈들, conftest의 가짜
# 임베딩과 벡터 차원.
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


# 정답이 한국어 페이지여도 같은 페이지의 영어 원문이 나오면 맞음으로 센다(페이지 단위 Hit, 교차언어 검색
# 대비). 2위에서 맞았으므로 Hit@2는 참, Hit@1은 거짓, 역순위 0.5.
def test_hits_count_the_other_translation_of_an_expected_page():
    expected = ["docs/ko/docs/tutorial/body.md"]
    ranked = ["docs/en/docs/tutorial/cors.md", "docs/en/docs/tutorial/body.md"]

    assert hit_at_k(ranked, expected, 2)
    assert not hit_at_k(ranked, expected, 1)
    assert reciprocal_rank(ranked, expected) == 0.5


# 한 언어만 검색하는 경우에는 경로를 그대로 비교하던 이전 정의와 값이 같아야 한다. 정답이 여럿이면 처음 맞은
# 순위로, 결과에 없으면 0으로 센다. 그래야 v12 이전 기록과 비교할 수 있다.
def test_single_language_results_score_exactly_as_before():
    expected = ["docs/ko/docs/a.md", "docs/ko/docs/b.md"]
    ranked = ["docs/ko/docs/c.md", "docs/ko/docs/b.md", "docs/ko/docs/a.md"]

    assert reciprocal_rank(ranked, expected) == 0.5
    assert hit_at_k(ranked, expected, 2) and not hit_at_k(ranked, expected, 1)
    assert reciprocal_rank(["docs/ko/docs/z.md"], expected) == 0.0


# force_exact_search가 이 세션의 enable_indexscan을 off로 바꾸는지 확인한다(--exact 실행의 바탕).
@pytest.mark.asyncio
async def test_exact_search_turns_off_index_scans_for_the_session(db_session):
    await force_exact_search(db_session)

    assert (await db_session.execute(text("SHOW enable_indexscan"))).scalar() == "off"


# '다른 모델'을 흉내 내는 가짜 임베딩: 같은 인터페이스지만 문서 벡터가 저장된 것과 무관하다. 저장 벡터 확인이
# 모델 불일치를 잡는지 볼 때 쓴다.
class OtherEmbeddingService(FakeEmbeddingService):
    """다른 모델 흉내: 인터페이스는 같고 벡터는 무관하다."""

    def __init__(self) -> None:
        self.model_name = "other-embedding"

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (EMBEDDING_DIM - 1) for _ in texts]


# 주어진 임베딩으로, 적재와 같은 입력(머리말 + 본문)을 임베딩한 청크 하나를 넣는다. 저장 벡터 확인은 이 입력을
# 다시 임베딩해 비교하므로 형식이 같아야 한다.
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


# 청크를 만든 모델과 같은 모델로 확인하면 통과하고 최소 코사인이 약 1.0이다.
@pytest.mark.asyncio
async def test_vector_check_passes_for_the_model_that_embedded_the_chunks(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    checked = await check_stored_vectors(db_session, FakeEmbeddingService(), "ko")

    assert checked["checked"] == 1
    assert checked["min_cosine"] > 0.999


# 다른 모델로 확인하면 VectorModelMismatch로 멈춰야 한다. DB와 모델을 엇갈려 짚으면 오류 없이 틀린 숫자만
# 나오기 때문에 넣은 확인이다.
@pytest.mark.asyncio
async def test_vector_check_refuses_a_database_embedded_by_another_model(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    with pytest.raises(VectorModelMismatch):
        await check_stored_vectors(db_session, OtherEmbeddingService(), "ko")


# 확인할 언어의 청크가 하나도 없어도 멈춘다(빈 DB나 잘못된 DB를 짚은 경우).
@pytest.mark.asyncio
async def test_vector_check_refuses_a_language_with_no_chunks(db_session):
    with pytest.raises(VectorModelMismatch):
        await check_stored_vectors(db_session, FakeEmbeddingService(), "en")


# retrieval.jsonl 한 행과 같은 모양의 가짜 기록. 점수 목록대로 결과를 만들고, hit_rank 위치의 경로를 정답으로
# 둔다(None이면 결과에 없는 정답).
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


# 기록에서 바닥값을 바꿔 지표를 다시 계산할 수 있는지 확인한다: 바닥값 0에서는 q2가 3위에서 맞지만, 0.3에서는
# 그 결과가 잘려 역순위 0이 되고 남은 결과가 2개라 short로 센다.
def test_metrics_at_a_floor_drop_results_under_it():
    records = [
        _record("q1", [0.9, 0.8, 0.7, 0.6, 0.5, 0.4], hit_rank=2),
        _record("q2", [0.5, 0.4, 0.29, 0.28, 0.27], hit_rank=3),
    ]

    at_zero = retrieval_runs.metrics(records, floor=0.0)
    at_shared = retrieval_runs.metrics(records, floor=0.3)

    assert at_zero["mrr"] == pytest.approx((1 / 2 + 1 / 3) / 2)
    assert at_zero["short"] == 0
    assert at_shared["mrr"] == pytest.approx((1 / 2 + 0) / 2)  # q2의 정답이 0.3 아래로 떨어졌다
    assert at_shared["short"] == 1  # q2는 결과가 2개만 남아 5개보다 적다


# 바닥값 규칙: 모든 문항이 0.3에서 5개 이상 남으면 공통 바닥값 0.3을 그대로 쓴다(docs/experiments.md v12 선택
# 1번).
def test_floor_rule_keeps_the_shared_floor_when_every_question_keeps_five():
    records = [_record("q1", [0.9, 0.8, 0.7, 0.6, 0.31, 0.2], hit_rank=1)]

    assert retrieval_runs.pick_floor(records) == 0.3


# 어느 문항이 5개 미만으로 남으면 후보 값을 낮춰 가며 모두 5개가 남는 가장 높은 값을 고른다. 원래 결과가
# 5개뿐인 q1은 그대로 통과한다.
def test_floor_rule_lowers_the_floor_until_every_question_keeps_five():
    records = [
        _record("q1", [0.9, 0.8, 0.7, 0.6, 0.5], hit_rank=1),
        _record("q2", [0.4, 0.3, 0.26, 0.22, 0.21, 0.1], hit_rank=1),
    ]

    # q2의 다섯 번째 점수는 0.21이다: 0.25면 결과가 3개로 줄고, 0.2면 5개가 남는다.
    assert retrieval_runs.pick_floor(records) == 0.2


# 두 실행 비교: 상위 청크 id가 바뀐 문항(q2)만 '순위 바뀜'으로 세고, 두 실행의 MRR을 함께 낸다(q2가 2위 →
# 1위라 0.75 → 1.0).
def test_comparing_two_runs_reports_questions_whose_ranking_changed():
    a = [_record("q1", [0.9, 0.8], hit_rank=1), _record("q2", [0.9, 0.8], hit_rank=2)]
    b = [_record("q1", [0.9, 0.8], hit_rank=1), _record("q2", [0.9, 0.85], hit_rank=1)]
    b[1]["results"][0]["chunk_id"] = "moved"

    diff = retrieval_runs.compare(a, b, top=10)

    assert diff["same_ranking"] == 1
    assert diff["changed_ids"] == ["q2"]
    assert diff["mrr_a"] == pytest.approx(0.75) and diff["mrr_b"] == pytest.approx(1.0)


# 정확 탐색으로 바꾼 뒤의 실행 계획에 Seq Scan이 있고 HNSW 인덱스가 없는지, 청크가 없는 언어는 빈 목록인지
# 확인한다. 리포트에 적는 계획이 실제 스캔 방식을 보여 주는지 고정한다.
@pytest.mark.asyncio
async def test_dense_plan_names_the_scan_and_exact_search_avoids_the_index(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    await force_exact_search(db_session)
    nodes = await dense_search_plan(db_session, "ko")

    assert any(node.startswith("Seq Scan on chunks") for node in nodes)
    assert not any("hnsw" in node for node in nodes)
    assert await dense_search_plan(db_session, "en") == []  # 계획을 세울 영어 청크가 없다
