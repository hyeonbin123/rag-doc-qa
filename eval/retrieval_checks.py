"""평가 스크립트가 측정을 시작하기 전에 DB에 대고 돌리는 확인들.

임베딩 비교(docs/experiments.md v12)에서는 같은 스크립트를 서로 다른 모델로 임베딩한 여러 DB에 돌리고,
모델은 환경 변수로 고른다. 한 모델로 만든 질문 벡터를 다른 모델의 벡터에 대고 재도 실패하지 않고 틀린
숫자만 나온다. check_stored_vectors가 이것을 잡는다.
"""

# [파일 역할] 검색·답변 평가 스크립트(eval/run_retrieval_eval.py, eval/run_answer_eval.py)가 측정을 시작하기
# 전에 DB 상태를 확인하는 도우미 모음이다.
# [왜 필요한가] v12 한국어 임베딩 비교에서는 후보 모델마다 복제 DB(ragdb_p1_<이름>)를 따로 만들고, 같은
# 스크립트를 환경 변수로 DB와 모델만 바꿔 돌렸다. DB와 모델을 엇갈려 짚어도 검색은 오류 없이 돌아가 틀린
# 숫자만 나오므로, 측정 전에 저장된 벡터가 지금 모델로 만든 것인지 확인하고 아니면 멈춘다(docs/experiments.md
# v12 '벡터 확인').
# [주요 구성] force_exact_search(인덱스 스캔을 꺼 정확 탐색으로 비교), check_stored_vectors(저장 벡터와 다시
# 만든 벡터의 cos 비교), dense_search_plan(플래너가 고른 스캔 방식 기록).
# [연결] eval/run_retrieval_eval.py가 세 함수를 모두, eval/run_answer_eval.py가 check_stored_vectors를 쓴다.
# tests/test_retrieval_eval.py가 동작을 고정한다.

from __future__ import annotations

import json
import math

# SQLAlchemy의 text()로 원시 SQL을 보내고, 평가 스크립트가 넘기는 비동기 세션(AsyncSession)을 그대로 받는다.
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# 앱과 같은 코드를 써야 비교가 의미가 있다: 적재 때와 똑같이 머리말을 붙인 임베딩 입력(build_embedding_text),
# 같은 임베딩 서비스, 앱이 실제로 보내는 dense 검색 SQL(dense_search_sql)을 가져온다.
from app.services.chunking import build_embedding_text
from app.services.embedding import EmbeddingService
from app.services.retrieval import dense_search_sql

# 같은 모델이면 다시 만든 벡터와 저장 벡터의 cos가 약 1.0이 나온다. 0.99 미만이면 다른 모델의 벡터로 보고
# 멈춘다(docs/experiments.md v12 '벡터 확인': cos ≥ 0.99).
MIN_COSINE = 0.99


# 저장 벡터와 모델이 맞지 않을 때 내는 전용 예외. 평가 스크립트는 이를 잡지 않으므로 측정이 시작되기 전에
# 실행이 끝난다.
class VectorModelMismatch(RuntimeError):
    """그 언어의 저장 벡터가 이번 실행이 쓸 모델로 만든 것이 아니다."""


# 이 세션에서만 인덱스 스캔을 끄는 함수. --exact 옵션일 때 eval/run_retrieval_eval.py가 부르며, 근사(HNSW)
# 결과와 정확 탐색 결과가 같은지 비교하는 기준 실행을 만든다(docs/experiments.md v12 '실행 계획').
# SET은 세션 범위라 다른 연결이나 앱에는 영향이 없다.
async def force_exact_search(db: AsyncSession) -> None:
    """이 세션의 벡터 검색을 HNSW 인덱스 스캔 대신 정확 탐색으로 바꾼다.

    인덱스 스캔을 끄면 플래너가 그 언어의 모든 행을 거리순으로 정렬한다. 이것이 근사 HNSW 탐색과 비교할
    정확한 상위 k개다.
    """
    await db.execute(text("SET enable_indexscan = off"))


# 두 벡터의 코사인 유사도. 3개 정도만 비교하므로 numpy 없이 순수 파이썬으로 계산한다. strict=True로 길이가
# 다르면(차원이 다른 모델) 바로 오류가 나게 한다.
def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


# `language` 청크 몇 개(기본 3개)를 지금 모델로 다시 임베딩해 저장 벡터와 비교하고, 결과를 dict로
# 돌려준다(리포트·meta에 기록됨).
# 출력: language, 모델 identity(이름·리비전·자르기 차원), 확인한 개수, 최소 cos. 최소 cos가 MIN_COSINE보다
# 낮거나 그 언어 청크가 없으면 VectorModelMismatch를 낸다.
# 교차언어(T3) 실행에서는 평가 스크립트가 영어 청크를 한국어 모델로 확인하도록 부른다(영어 청크도 다국어
# 모델로 적재한 복제 DB이기 때문).
async def check_stored_vectors(
    db: AsyncSession, embedder: EmbeddingService, language: str, sample: int = 3
) -> dict:
    """`language` 청크 몇 개를 다시 임베딩해 저장된 벡터와 비교한다.

    적재는 build_embedding_text(heading_path, content)를 임베딩하므로, 같은 모델이면 저장된 벡터가 다시
    나온다(cos 약 1.0). 다른 모델의 벡터와는 상관이 없다.
    """
    # ORDER BY id로 항상 같은 청크를 골라 실행마다 같은 확인을 한다. embedding::text는 pgvector 값을
    # '[0.1,0.2,...]' 문자열로 받아 아래에서 json.loads로 리스트로 바꾸기 위한 것이다.
    rows = (
        await db.execute(
            text(
                "SELECT heading_path, content, embedding::text AS embedding FROM chunks "
                "WHERE language = :language ORDER BY id LIMIT :n"
            ),
            {"language": language, "n": sample},
        )
    ).all()
    if not rows:
        raise VectorModelMismatch(f"no {language} chunks in this database")
    # 적재(ingestion)와 똑같이 문서용(passage) 임베딩 함수와 같은 입력 형식을 써야 같은 벡터가 나온다. 질문용
    # 함수를 쓰면 접두사가 달라 같은 모델이어도 cos가 낮아진다.
    fresh = embedder.embed_passages([build_embedding_text(r.heading_path or "", r.content) for r in rows])
    cosines = [_cosine(json.loads(r.embedding), v) for r, v in zip(rows, fresh, strict=True)]
    result = {
        "language": language,
        "model": embedder.identity,
        "checked": len(rows),
        "min_cosine": round(min(cosines), 6),
    }
    # 하나라도 기준 아래면 DATABASE_URL이나 모델 설정이 틀렸을 가능성을 오류 문장에 함께 적어 원인을 바로 찾게
    # 한다.
    if result["min_cosine"] < MIN_COSINE:
        raise VectorModelMismatch(
            f"stored {language} vectors were not made by {embedder.identity} "
            f"(cosine {result['min_cosine']} < {MIN_COSINE}); wrong DATABASE_URL or model?"
        )
    return result


# 앱의 dense 검색 SQL에 EXPLAIN을 붙여 Postgres가 고른 스캔 노드 이름 목록을 돌려준다. 리포트에 실행 계획을
# 남기는 데 쓴다.
# 왜 기록하나: 2026-10-04 본 DB에서 dense 검색이 HNSW가 아니라 Seq Scan + Sort(정확 탐색)로 계획되는 것을
# 확인했고, v8 때와 달라진 원인은 확인하지 않았다. 그래서 리포트마다 계획을 적어 '근사 오차를 잰 것인지'를 알
# 수 있게 한다(docs/experiments.md v12).
# 그 언어의 청크가 없으면 빈 목록을 돌려준다.
async def dense_search_plan(db: AsyncSession, language: str, top_k: int = 10) -> list[str]:
    """Postgres가 `language`의 dense 검색에 고른 스캔 노드들.

    "Index Scan using chunks_embedding_<language>_hnsw_idx"는 근사 HNSW 탐색이고, Sort 아래의
    "Seq Scan on chunks"는 정확 탐색이다. 언어마다 청크가 수백 개 수준이면 플래너가 정확 탐색을 고를 수
    있다. 질의 대신 저장된 벡터 하나를 쓴다.
    """
    # 실제 질문 벡터 대신 저장된 벡터 하나를 질의로 쓴다. 계획은 값보다 SQL 모양과 테이블 통계로 정해지므로
    # 이것으로 충분하다.
    vector = (
        await db.execute(
            text("SELECT embedding::text FROM chunks WHERE language = :language ORDER BY id LIMIT 1"),
            {"language": language},
        )
    ).scalar()
    if vector is None:
        return []
    plan = await db.execute(
        text("EXPLAIN " + dense_search_sql(language)), {"qvec": vector, "top_k": top_k}
    )
    # EXPLAIN 출력 줄에서 비용 괄호 앞의 노드 이름만 잘라 내고, 스캔 노드와 Sort만 남긴다(예: 'Index Scan
    # using chunks_embedding_ko_hnsw_idx on chunks c', 'Seq Scan on chunks c').
    nodes = [line.split("(cost")[0].replace("->", "").strip() for (line,) in plan if "(cost" in line]
    return [node for node in nodes if "Scan" in node or node == "Sort"]
