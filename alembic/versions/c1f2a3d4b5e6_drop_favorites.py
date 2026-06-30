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
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if not insp.has_table("meal_plan_expenses") and insp.has_table("meal_plans"):
        op.create_table(
            "meal_plan_expenses",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "meal_plan_id",
                sa.Integer(),
                sa.ForeignKey("meal_plans.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "restaurant_id",
                sa.Integer(),
                sa.ForeignKey("restaurants.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("amount", sa.Integer(), nullable=False),
            sa.Column("spent_on", sa.Date(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )
        op.create_index("ix_meal_plan_expenses_user_id", "meal_plan_expenses", ["user_id"])
        op.create_index(
            "ix_meal_plan_expenses_meal_plan_id", "meal_plan_expenses", ["meal_plan_id"]
        )
        op.create_index("ix_meal_plan_expenses_spent_on", "meal_plan_expenses", ["spent_on"])

    if insp.has_table("favorites"):
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
