"""add restaurants and daily_picks

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-05-19

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "restaurants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("name_key", sa.String(length=128), nullable=False),
        sa.Column("category_slug", sa.String(length=32), nullable=False),
        sa.Column("category_label", sa.String(length=32), nullable=False),
        sa.Column("district", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=512), nullable=False),
        sa.Column("closed_weekdays", sa.ARRAY(sa.Integer()), server_default="{}", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_restaurants_name"), "restaurants", ["name"], unique=True)
    op.create_index(op.f("ix_restaurants_name_key"), "restaurants", ["name_key"], unique=False)
    op.create_index(
        op.f("ix_restaurants_category_slug"), "restaurants", ["category_slug"], unique=False
    )

    op.create_table(
        "daily_picks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pick_date", sa.Date(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pick_date", "rank", name="uq_daily_pick_date_rank"),
        sa.UniqueConstraint("pick_date", "restaurant_id", name="uq_daily_pick_date_restaurant"),
    )
    op.create_index(op.f("ix_daily_picks_pick_date"), "daily_picks", ["pick_date"], unique=False)
    op.create_index(
        op.f("ix_daily_picks_restaurant_id"), "daily_picks", ["restaurant_id"], unique=False
    )


def downgrade() -> None:
    op.drop_table("daily_picks")
    op.drop_table("restaurants")
