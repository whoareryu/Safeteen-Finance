"""gourmet domain: restaurants, favorites, meal_plans, daily_recommendations

Revision ID: d1e2f3a4b5c6
Revises:
Create Date: 2026-05-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("biz_number", sa.String(length=48), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("store_name", sa.Text(), server_default="", nullable=False),
        sa.Column("branch_name", sa.Text(), server_default="", nullable=False),
        sa.Column("category_slug", sa.String(length=32), nullable=False),
        sa.Column("category_label", sa.String(length=32), server_default="", nullable=False),
        sa.Column("district", sa.String(length=128), server_default="", nullable=False),
        sa.Column("sigungu_name", sa.String(length=32), server_default="", nullable=False),
        sa.Column("road_address", sa.Text(), server_default="", nullable=False),
        sa.Column("parcel_address", sa.Text(), server_default="", nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("avg_price", sa.Integer(), nullable=True),
        sa.Column("signature_menu", sa.String(length=256), server_default="", nullable=False),
        sa.Column(
            "ai_tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="[]",
            nullable=False,
        ),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("image_url", sa.String(length=512), server_default="", nullable=False),
        sa.Column("biz_mid_name", sa.String(length=64), server_default="", nullable=False),
        sa.Column("biz_minor_name", sa.String(length=128), server_default="", nullable=False),
        sa.Column("ksic_name", sa.String(length=256), server_default="", nullable=False),
        sa.Column("view_count", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("biz_number"),
    )
    op.create_index("ix_restaurants_biz_number", "restaurants", ["biz_number"], unique=True)
    op.create_index("ix_restaurants_category_id", "restaurants", ["category_slug", "id"])
    op.create_index(
        "ix_restaurants_category_district_id",
        "restaurants",
        ["category_slug", "district", "id"],
    )
    op.create_index(
        "ix_restaurants_category_price_id",
        "restaurants",
        ["category_slug", "avg_price", "id"],
    )
    op.create_index("ix_restaurants_district", "restaurants", ["district"])
    op.create_index(op.f("ix_restaurants_name"), "restaurants", ["name"])
    op.create_index(op.f("ix_restaurants_category_slug"), "restaurants", ["category_slug"])
    op.create_index(op.f("ix_restaurants_avg_price"), "restaurants", ["avg_price"])

    op.create_table(
        "favorites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "restaurant_id", name="uq_favorites_user_restaurant"),
    )
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"])
    op.create_index(op.f("ix_favorites_restaurant_id"), "favorites", ["restaurant_id"])

    op.create_table(
        "meal_plans",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("monthly_budget", sa.Integer(), nullable=False),
        sa.Column("spent_amount", sa.Integer(), server_default="0", nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_plans_user_id"), "meal_plans", ["user_id"])
    op.create_index(op.f("ix_meal_plans_period_start"), "meal_plans", ["period_start"])
    op.create_index(op.f("ix_meal_plans_period_end"), "meal_plans", ["period_end"])

    op.create_table(
        "daily_recommendations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("meal_plan_id", sa.Integer(), nullable=True),
        sa.Column("recommended_on", sa.Date(), nullable=False),
        sa.Column("pick_reason", sa.Text(), server_default="", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["user.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "recommended_on", name="uq_daily_rec_user_date"),
    )
    op.create_index(
        op.f("ix_daily_recommendations_user_id"), "daily_recommendations", ["user_id"]
    )
    op.create_index(
        op.f("ix_daily_recommendations_restaurant_id"),
        "daily_recommendations",
        ["restaurant_id"],
    )
    op.create_index(
        op.f("ix_daily_recommendations_recommended_on"),
        "daily_recommendations",
        ["recommended_on"],
    )


def downgrade() -> None:
    op.drop_table("daily_recommendations")
    op.drop_table("meal_plans")
    op.drop_table("favorites")
    op.drop_index("ix_restaurants_district", table_name="restaurants")
    op.drop_index("ix_restaurants_category_price_id", table_name="restaurants")
    op.drop_index("ix_restaurants_category_district_id", table_name="restaurants")
    op.drop_index("ix_restaurants_category_id", table_name="restaurants")
    op.drop_table("restaurants")
