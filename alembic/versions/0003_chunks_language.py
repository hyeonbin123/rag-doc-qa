"""add language to chunks

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-12

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Every existing row is English: until now only docs/en/docs was ingested.
    op.add_column(
        "chunks",
        sa.Column("language", sa.String(8), nullable=False, server_default="en"),
    )


def downgrade() -> None:
    op.drop_column("chunks", "language")
