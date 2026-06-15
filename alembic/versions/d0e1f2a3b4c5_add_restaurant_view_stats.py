"""add restaurant_view_stats

Revision ID: d0e1f2a3b4c5
Revises: c9d0e1f2a3b4
Create Date: 2026-05-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a3b4c5"
down_revision: Union[str, Sequence[str], None] = "c9d0e1f2a3b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restaurant_view_stats",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("view_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("first_viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_viewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("restaurant_id"),
    )
    op.create_index(
        op.f("ix_restaurant_view_stats_restaurant_id"),
        "restaurant_view_stats",
        ["restaurant_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_restaurant_view_stats_view_count"),
        "restaurant_view_stats",
        ["view_count"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_restaurant_view_stats_view_count"), table_name="restaurant_view_stats"
    )
    op.drop_index(
        op.f("ix_restaurant_view_stats_restaurant_id"),
        table_name="restaurant_view_stats",
    )
    op.drop_table("restaurant_view_stats")
