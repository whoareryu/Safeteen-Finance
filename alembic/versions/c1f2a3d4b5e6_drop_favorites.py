"""즐겨찾기(favorites) 기능 제거 — 비스펙(기획서 외) 대청소.

Revision ID: c1f2a3d4b5e6
Revises: 3462e2ac1573
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1f2a3d4b5e6"
down_revision: Union[str, Sequence[str], None] = "3462e2ac1573"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("favorites"):
        op.drop_table("favorites")


def downgrade() -> None:
    if not sa.inspect(op.get_bind()).has_table("favorites"):
        op.create_table(
            "favorites",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "restaurant_id",
                sa.Integer(),
                sa.ForeignKey("restaurants.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )
