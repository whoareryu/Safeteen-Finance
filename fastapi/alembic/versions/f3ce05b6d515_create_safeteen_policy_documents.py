"""create safeteen_policy_documents (RAG 정책 매칭용 벡터 테이블)

Revision ID: f3ce05b6d515
Revises: e2f3a4b5c6d7
Create Date: 2026-08-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "f3ce05b6d515"
down_revision: Union[str, Sequence[str], None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

POLICY_EMBEDDING_DIM = 768


def upgrade() -> None:
    op.create_table(
        "safeteen_policy_documents",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("official_link", sa.String(), nullable=False),
        sa.Column("embedding", Vector(POLICY_EMBEDDING_DIM), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("title"),
    )


def downgrade() -> None:
    op.drop_table("safeteen_policy_documents")
