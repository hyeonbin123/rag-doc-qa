"""임베딩 비교(docs/experiments.md v12)를 위한 검색 평가 도우미들을 검증한다."""

# [테스트 묶음] v12 한국어 임베딩 비교를 위해 넓힌 검색 평가 하네스의 테스트: 페이지 단위
# Hit·MRR(eval/run_retrieval_eval.py), 측정 전 확인(eval/retrieval_checks.py의 정확 탐색 전환·저장 벡터
# 확인·실행 계획), 기록 분석(eval/retrieval_runs.py의 바닥값 규칙·두 실행 비교).
# [왜 중요한가] 이 도구들의 숫자로 한국어 임베딩 교체를 결정했다(docs/experiments.md v12, v13 단계 B). Hit
# 정의가 이전과 달라지거나, 다른 모델의 DB를 그대로 재거나, 바닥값 규칙이 틀리면 결정이 틀어진다.
# [import] SQLAlchemy text는 세션 설정(SHOW enable_indexscan)을 직접 읽는 데 쓴다. async_sessionmaker는 평가
# main이 여는 DB 세션을 테스트 DB로 바꿔 끼울 때 쓴다.
# event는 평가 실행이 엔진에 보낸 문장과 트랜잭션 끝을 순서대로 모으는 데, EXACT_SEARCH_PIN_SQL은 그중 앱의
# 정확 탐색 고정 문장을 알아보는 데 쓴다(2026-11-03 재적재 전 보충).

import argparse
import hashlib
from datetime import UTC, datetime

import pytest
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import async_sessionmaker

# 테스트 데이터로 넣을 문서·청크 모델과 적재와 같은 임베딩 입력 함수, 테스트 대상 평가 모듈들, conftest의 가짜
# 임베딩과 벡터 차원.
from app.models.chunk import Chunk
from app.models.document import Document
from app.services.chunking import build_embedding_text
from app.services.retrieval import EXACT_SEARCH_PIN_SQL
from eval import retrieval_runs, run_retrieval_eval
from eval.common import corpus_line, corpus_snapshot, dataset_sha256, read_json, write_jsonl
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


# 앱과 같은 고정 아래의 실행 계획(dense_search_plan 기본값)에 Seq Scan이 있고 HNSW 인덱스가 없는지, 청크가
# 없는 언어는 빈 목록인지 확인한다. 리포트에 적는 계획이 실제 스캔 방식을 보여 주는지 고정한다. 2026-11-03부터
# 기본값은 --exact(force_exact_search) 없이도 앱처럼 이 트랜잭션에 고정을 걸고 EXPLAIN하므로 그 뒤 같은
# 트랜잭션의 enable_indexscan은 off이고, SET LOCAL이라 commit하면 풀린다. --exact만 건 세션의 pinned=False
# 계획도 노드 목록의 모양을 함께 본다. 다만 테스트 DB는 모델(create_all)로 만들어 HNSW 인덱스가 없으므로 이
# 계획은 --exact와 상관없이 Seq Scan이고, 이 단언은 --exact의 효과를 확인하지 않는다(그것은 SHOW로 보는
# test_exact_search_turns_off_index_scans_for_the_session 등이 지키고, 플래너가 HNSW를 고르는 조건은
# tests/test_retrieval.py가 만든다). 고치기 전 이 테스트는 force_exact_search를 먼저 부른 뒤의 계획만 봤다.
@pytest.mark.asyncio
async def test_dense_plan_names_the_scan_and_defaults_to_the_apps_exact_pin(db_session):
    await _seed_embedded_chunk(db_session, FakeEmbeddingService())

    nodes = await dense_search_plan(db_session, "ko")

    assert any(node.startswith("Seq Scan on chunks") for node in nodes)
    assert not any("hnsw" in node for node in nodes)
    assert (await db_session.execute(text("SHOW enable_indexscan"))).scalar() == "off"
    await db_session.commit()
    assert (await db_session.execute(text("SHOW enable_indexscan"))).scalar() == "on"

    await force_exact_search(db_session)
    exact_nodes = await dense_search_plan(db_session, "ko", pinned=False)
    assert any(node.startswith("Seq Scan on chunks") for node in exact_nodes)
    assert not any("hnsw" in node for node in exact_nodes)
    assert await dense_search_plan(db_session, "en") == []  # 계획을 세울 영어 청크가 없다


# 질문셋 해시는 줄 끝을 LF로 맞춘 바이트의 sha256이다. Windows에서 core.autocrlf로 CRLF 체크아웃을 해도 같은
# 커밋의 같은 질문셋이면 같은 값이 나와야 기록끼리 비교할 수 있다.
def test_dataset_sha256_ignores_crlf_checkouts(tmp_path):
    content = '{"id": "a"}\n{"id": "b"}\n'
    lf, crlf = tmp_path / "lf.jsonl", tmp_path / "crlf.jsonl"
    lf.write_bytes(content.encode("utf-8"))
    crlf.write_bytes(content.replace("\n", "\r\n").encode("utf-8"))
    assert dataset_sha256(lf) == dataset_sha256(crlf) == hashlib.sha256(content.encode("utf-8")).hexdigest()


# 코퍼스 요약: 문서의 원본 커밋(source_commit_sha)별 문서 수, 마지막 적재 시각(max fetched_at), 언어별 청크
# 수. 다른 커밋으로 일부만 다시 적재한 DB는 커밋이 둘로 보인다. 리포트 머리 한 줄은 커밋을 7자리로 줄여
# 적는다.
@pytest.mark.asyncio
async def test_corpus_snapshot_counts_documents_per_source_commit_and_chunks_per_language(db_session):
    embedder = FakeEmbeddingService()
    seeds = (
        ("docs/en/docs/a.md", "a" * 40, datetime(2026, 10, 1, tzinfo=UTC), ["en", "en"]),
        ("docs/en/docs/b.md", "a" * 40, datetime(2026, 10, 2, tzinfo=UTC), []),
        ("docs/ko/docs/a.md", "b" * 40, datetime(2026, 10, 3, 4, 5, tzinfo=UTC), ["ko"]),
    )
    for path, sha, fetched_at, languages in seeds:
        document = Document(
            source_path=path, title="A", source_commit_sha=sha, content_hash="h", fetched_at=fetched_at
        )
        db_session.add(document)
        await db_session.flush()
        for index, language in enumerate(languages):
            db_session.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=index,
                    heading_path="A",
                    content=f"본문 {index}",
                    token_count=3,
                    embedding=embedder.embed_passages([f"본문 {index}"])[0],
                    language=language,
                )
            )
    await db_session.commit()

    snapshot = await corpus_snapshot(db_session)

    assert snapshot == {
        "documents_by_source_commit": {"a" * 40: 2, "b" * 40: 1},
        "last_fetched_at": "2026-10-03T04:05:00+00:00",
        "chunks_by_language": {"en": 2, "ko": 1},
    }
    assert corpus_line(snapshot) == (
        "- corpus: source commits aaaaaaa (2 documents), bbbbbbb (1 document); "
        "last fetched 2026-10-03T04:05:00+00:00; chunks en 2, ko 1"
    )
    assert corpus_line(
        {"documents_by_source_commit": {}, "last_fetched_at": None, "chunks_by_language": {}}
    ) == ("- corpus: no documents")


# 검색 평가 실행 한 번(main)을 테스트 DB와 가짜 임베딩으로 돌린다. meta에 질문셋 파일마다의 sha256과 DB 코퍼스
# 요약이 남고, 리포트 머리의 database 줄 바로 아래에 코퍼스 줄이 있다.
# 2026-11-03부터 리포트의 탐색 방식 줄은 앱과 같은 정확 탐색 고정을 적고(--exact 없음), meta의 dense_plans는
# 고정 아래의 계획(HNSW 노드 없음)이다.
@pytest.mark.asyncio
async def test_retrieval_eval_records_question_set_hashes_and_the_corpus(
    db_engine, db_session, tmp_path, monkeypatch
):
    embedder = FakeEmbeddingService()
    await _seed_embedded_chunk(db_session, embedder, language="en")
    datasets = []
    for name in ("qa_one.jsonl", "qa_two.jsonl"):
        path = tmp_path / name
        write_jsonl(
            path,
            [
                {
                    "id": f"{name[:6]}1",
                    "question": f"Where are path parameters declared ({name})?",
                    "expected_source_paths": ["docs/en/docs/a.md"],
                    "reference_answer": "In the path string.",
                }
            ],
        )
        datasets.append(path)

    def write_report_here(filename: str, content: str):
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return path

    monkeypatch.setattr(run_retrieval_eval, "async_session_maker", async_sessionmaker(db_engine))
    monkeypatch.setattr(run_retrieval_eval, "get_embedding_service", lambda language: embedder)
    monkeypatch.setattr(run_retrieval_eval, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(run_retrieval_eval, "write_report", write_report_here)
    args = argparse.Namespace(
        top_k=10,
        tag="prov",
        mode="dense",
        dataset=datasets,
        lexical_weight=0.75,
        rerank_pool=None,
        reranker_model=None,
        score_floor=None,
        cross_lingual=False,
        exact=False,
        no_vector_check=False,
    )

    await run_retrieval_eval.main(args)

    meta = read_json(tmp_path / "runs" / "prov.retrieval.meta.json")
    assert meta["dataset_sha256"] == {path.name: dataset_sha256(path) for path in datasets}
    assert meta["corpus"]["documents_by_source_commit"] == {"x": 1}
    assert meta["corpus"]["chunks_by_language"] == {"en": 1}
    assert meta["exact"] is False
    assert meta["dense_plans"]["en"] and not any("hnsw" in node for node in meta["dense_plans"]["en"])
    report = next(tmp_path.glob("retrieval_eval_prov_*.md")).read_text(encoding="utf-8").splitlines()
    at = next(i for i, line in enumerate(report) if line.startswith("- database:"))
    assert report[at + 1].startswith("- corpus: source commit x (1 document); last fetched ")
    search_line = "- search: dense exact, pinned like the app; dense plan: en "
    assert any(line.startswith(search_line) for line in report)


# 2026-11-03 재적재 전 보충: 검색 평가는 실행 계획을 먼저 기록하고 rollback해 그 기록이 건 고정을 끝낸 뒤, 새
# 트랜잭션에서 문항을 검색한다(eval/run_retrieval_eval.py의 main 주석). 실제 검색 함수(retrieve)를 감싸
# 문항마다 검색 직전·직후의 enable_indexscan을 읽는다. --exact가 없으면 첫 검색 직전은 on이고(계획 기록의
# 고정이 남지 않음) 직후는 검색 함수 자신의 고정으로 off다. --exact면 rollback 뒤에 세션 전체 설정을 걸므로 첫
# 검색 직전부터 off다(rollback 앞에 걸면 rollback이 그 설정까지 지워 on이 된다). 둘째 문항은 첫 검색의 고정이
# 같은 트랜잭션에 남아 직전부터 off다. 엔진에 보낸 문장과 트랜잭션 끝으로는 계획 기록(EXPLAIN)과 첫 검색
# 사이에 트랜잭션이 끝나는지, 문항마다 dense SQL 바로 앞에 고정 문장이 가는지, 세션 SET이 --exact일 때만 한
# 번인지 본다. 고치기 전(계획 기록과 문항 검색이 한 트랜잭션)에는 --exact 없이도 첫 검색 직전이 off였다.
# 테스트 DB에는 HNSW 인덱스가 없으므로 고정이 HNSW를 이기는지는 tests/test_retrieval.py가 본다.
@pytest.mark.asyncio
@pytest.mark.parametrize("exact", [True, False])
async def test_retrieval_eval_searches_outside_the_transaction_the_plan_record_pinned(
    db_engine, db_session, tmp_path, monkeypatch, exact
):
    embedder = FakeEmbeddingService()
    await _seed_embedded_chunk(db_session, embedder, language="en")
    dataset = tmp_path / "qa_dev.jsonl"
    write_jsonl(
        dataset,
        [
            {
                "id": item_id,
                "question": f"Where are path parameters declared ({item_id})?",
                "expected_source_paths": ["docs/en/docs/a.md"],
                "reference_answer": "In the path string.",
            }
            for item_id in ("q001", "q002")
        ],
    )
    around: list[tuple[str, str]] = []
    real_retrieve = run_retrieval_eval.retrieve

    async def retrieve_reading_the_setting_around_it(db, *args, **kwargs):
        before = (await db.execute(text("SHOW enable_indexscan"))).scalar()
        chunks = await real_retrieve(db, *args, **kwargs)
        around.append((before, (await db.execute(text("SHOW enable_indexscan"))).scalar()))
        return chunks

    def write_report_here(filename: str, content: str):
        path = tmp_path / filename
        path.write_text(content, encoding="utf-8")
        return path

    monkeypatch.setattr(run_retrieval_eval, "retrieve", retrieve_reading_the_setting_around_it)
    monkeypatch.setattr(run_retrieval_eval, "async_session_maker", async_sessionmaker(db_engine))
    monkeypatch.setattr(run_retrieval_eval, "get_embedding_service", lambda language: embedder)
    monkeypatch.setattr(run_retrieval_eval, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(run_retrieval_eval, "write_report", write_report_here)
    args = argparse.Namespace(
        top_k=10,
        tag="pinned",
        mode="dense",
        dataset=[dataset],
        lexical_weight=0.75,
        rerank_pool=None,
        reranker_model=None,
        score_floor=None,
        cross_lingual=False,
        exact=exact,
        no_vector_check=False,
    )
    sent: list[str] = []

    def record_statement(conn, cursor, statement, parameters, context, executemany):
        sent.append(statement)

    def record_end(conn):
        sent.append("<transaction end>")

    listeners = [
        ("before_cursor_execute", record_statement),
        ("commit", record_end),
        ("rollback", record_end),
    ]
    for name, listener in listeners:
        event.listen(db_engine.sync_engine, name, listener)
    try:
        await run_retrieval_eval.main(args)
    finally:
        for name, listener in listeners:
            event.remove(db_engine.sync_engine, name, listener)

    assert around == [("off" if exact else "on", "off"), ("off", "off")]
    explains = [i for i, s in enumerate(sent) if s.lstrip().startswith("EXPLAIN")]
    searches = [i for i, s in enumerate(sent) if "<=>" in s and not s.lstrip().startswith("EXPLAIN")]
    assert len(explains) == 1 and len(searches) == 2
    assert "<transaction end>" in sent[explains[0] : searches[0]]
    assert [sent[i - 1] for i in searches] == [EXACT_SEARCH_PIN_SQL] * 2
    assert sent.count("SET enable_indexscan = off") == (1 if exact else 0)
