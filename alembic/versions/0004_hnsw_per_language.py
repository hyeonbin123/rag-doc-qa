"""one HNSW index per docs language

English and Korean chunks are embedded by different models (bge-small-en and
multilingual-e5-small), so their vectors live in different spaces and must never be
navigated as one graph. Each query filters on one language, and a partial index per
language lets it scan only that language's graph.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-12

"""
from collections.abc import Sequence

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

LANGUAGES = ("en", "ko")
HNSW = "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"


def upgrade() -> None:
    op.execute("DROP INDEX IF EXISTS chunks_embedding_hnsw_idx")
    for language in LANGUAGES:
        op.execute(
            f"CREATE INDEX chunks_embedding_{language}_hnsw_idx ON chunks {HNSW} "
            f"WHERE language = '{language}'"
        )


def downgrade() -> None:
    for language in LANGUAGES:
        op.execute(f"DROP INDEX IF EXISTS chunks_embedding_{language}_hnsw_idx")
    op.execute(f"CREATE INDEX chunks_embedding_hnsw_idx ON chunks {HNSW}")
