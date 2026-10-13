"""one HNSW index per docs language

English and Korean chunks are embedded by different models (bge-small-en and
multilingual-e5-small), so their vectors live in different spaces and must never be
navigated as one graph. Each query filters on one language, and a partial index per
language lets it scan only that language's graph.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-12

"""
# [파일 역할] 0001의 전체 공용 HNSW 인덱스를 지우고, 언어마다 WHERE language = '<언어>' 조건이 붙은
# 부분(partial) HNSW 인덱스를 하나씩 만든다.
# [설계 이유] 위 docstring처럼 두 언어의 벡터는 다른 모델이 만든 다른 공간이라 한 그래프로 탐색하면 안 된다.
# 검색 SQL은 언어 값을 리터럴로 넣어(app/services/retrieval.py의 _language_sql) 플래너가 그 언어의 부분
# 인덱스를 고를 수 있게 한다. docs/experiments.md v8에 실행 계획으로 영어는 chunks_embedding_en_hnsw_idx,
# 한국어는 chunks_embedding_ko_hnsw_idx를 쓰는 것을 확인했다고 적혀 있다.
# [참고] docstring의 한국어 모델 이름(multilingual-e5-small)은 작성 당시 기준이다. v13 단계 B부터 한국어 기본
# 모델은 Granite R2 311M(384차원으로 자름)이지만 차원과 언어 분리 구조는 같다.
# [주의] 이 인덱스들은 마이그레이션에만 있고 앱 모델에는 선언돼 있지 않다. 그래서 테스트가 create_all로 만든
# 스키마에는 HNSW 인덱스가 없다.

from collections.abc import Sequence

from alembic import op

# 리비전 사슬: 0003 다음.
revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# 인덱스를 만들 언어 목록. 앱의 SUPPORTED_LANGUAGES(app/services/language.py)와 같은 값이지만, 마이그레이션은
# 그 시점의 스키마를 고정해야 하므로 직접 적는다.
# HNSW: 0001과 같은 인덱스 정의(코사인 거리, m=16, ef_construction=64)를 문자열로 재사용한다.
LANGUAGES = ("en", "ko")
HNSW = "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"


def upgrade() -> None:
    # 공용 인덱스를 먼저 지우고 언어별로 다시 만든다. f-string으로 SQL을 만들지만 들어가는 값은 위 상수
    # 목록뿐이라 외부 입력이 섞이지 않는다.
    op.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw_idx")
    for language in LANGUAGES:
        op.execute(
            f"CREATE INDEX chunks_embedding_{language}_hnsw_idx ON chunks {HNSW} "
            f"WHERE language = '{language}'"
        )


def downgrade() -> None:
    # 되돌리기: 언어별 인덱스를 지우고 0001의 공용 인덱스를 다시 만든다.
    for language in LANGUAGES:
        op.execute(f"DROP INDEX IF EXISTS chunks_embedding_{language}_hnsw_idx")
    op.execute(f"CREATE INDEX chunks_embedding_hnsw_idx ON chunks {HNSW}")
