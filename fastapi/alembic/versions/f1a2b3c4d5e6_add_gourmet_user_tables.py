"""GourmetMate 신규 사용자 테이블 — user_preferences, meal_plan_expenses, restaurant_visits.

온보딩 취향 / 식비 지출 / GPS 방문 (기획서 3-1·4-2·4-3).
운영 DB에는 이미 직접 생성돼 있을 수 있어 upgrade 는 멱등(존재 시 건너뜀)으로 둔다.

Revision ID: f1a2b3c4d5e6
Revises: b1c2d3e4f5a6
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if not _has_table("user_preferences"):
        op.create_table(
            "user_preferences",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
                unique=True,
            ),
            sa.Column(
                "genre_ranking",
                postgresql.JSONB(),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column("dining_mode", sa.String(16), nullable=False, server_default=""),
            sa.Column("portion", sa.String(16), nullable=False, server_default=""),
            sa.Column(
                "allergies",
                postgresql.JSONB(),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "avoid_foods",
                postgresql.JSONB(),
                nullable=False,
                server_default=sa.text("'[]'::jsonb"),
            ),
            sa.Column(
                "use_budget",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("monthly_budget", sa.Integer(), nullable=True),
        )
        op.create_index(
            "ix_user_preferences_user_id", "user_preferences", ["user_id"]
        )

    if not _has_table("meal_plan_expenses") and _has_table("meal_plans"):
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
        op.create_index(
            "ix_meal_plan_expenses_user_id", "meal_plan_expenses", ["user_id"]
        )
        op.create_index(
            "ix_meal_plan_expenses_meal_plan_id", "meal_plan_expenses", ["meal_plan_id"]
        )
        op.create_index(
            "ix_meal_plan_expenses_spent_on", "meal_plan_expenses", ["spent_on"]
        )

    if not _has_table("restaurant_visits"):
        op.create_table(
            "restaurant_visits",
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
            sa.Column("rating", sa.Integer(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column(
                "visited_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )
        op.create_index(
            "ix_restaurant_visits_user_id", "restaurant_visits", ["user_id"]
        )
        op.create_index(
            "ix_restaurant_visits_restaurant_id",
            "restaurant_visits",
            ["restaurant_id"],
        )


def downgrade() -> None:
    for table in ("restaurant_visits", "meal_plan_expenses", "user_preferences"):
        if _has_table(table):
            op.drop_table(table)
