"""add team_embedding — RAG 시맨틱 검색용 벡터 컬럼 (team)

Revision ID: f3a4b5c6d7e8
Revises: c9d122a45661
Create Date: 2026-07-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = "c9d122a45661"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TEAM_EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.add_column(
        "team",
        sa.Column("team_embedding", Vector(TEAM_EMBEDDING_DIM), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("team", "team_embedding")
