"""add search_query_logs — SearchQueryLog ORM에 대응하는 테이블 누락분 생성.

Revision ID: 81c39ada7703
Revises: a4b5c6d7e8f9
Create Date: 2026-07-13

"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "81c39ada7703"
down_revision: Union[str, Sequence[str], None] = "a4b5c6d7e8f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "search_query_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("query", sa.String(length=128), nullable=False),
        sa.Column("query_normalized", sa.String(length=128), nullable=False),
        sa.Column("result_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_search_query_logs_query"), "search_query_logs", ["query"], unique=False
    )
    op.create_index(
        op.f("ix_search_query_logs_query_normalized"),
        "search_query_logs",
        ["query_normalized"],
        unique=False,
    )
    op.create_index(
        op.f("ix_search_query_logs_created_at"),
        "search_query_logs",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_search_query_logs_created_at"), table_name="search_query_logs")
    op.drop_index(
        op.f("ix_search_query_logs_query_normalized"), table_name="search_query_logs"
    )
    op.drop_index(op.f("ix_search_query_logs_query"), table_name="search_query_logs")
    op.drop_table("search_query_logs")
