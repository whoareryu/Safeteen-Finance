"""drop tutorial_plants and pixabay_photo_caches (식집사 튜토리얼 기능 제거)

Revision ID: b2c3d4e5f6a7
Revises: e1f2a4b5c6d7
Create Date: 2026-08-02

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "e1f2a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("pixabay_photo_caches")
    op.drop_index("ix_tutorial_plants_owner_user_id", table_name="tutorial_plants")
    op.drop_table("tutorial_plants")


def downgrade() -> None:
    op.create_table(
        "tutorial_plants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("species_name", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("growth_stage", sa.String(length=10), nullable=False),
        sa.Column("soil_moisture_pct", sa.Float(), nullable=False),
        sa.Column("nutrient_pct", sa.Float(), nullable=False),
        sa.Column("light_position", sa.String(length=10), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("last_watered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_fertilized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_light_moved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_weather_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tutorial_plants_owner_user_id", "tutorial_plants", ["owner_user_id"])

    op.create_table(
        "pixabay_photo_caches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("species_name", sa.String(), nullable=False),
        sa.Column("growth_stage", sa.String(length=10), nullable=False),
        sa.Column("status_key", sa.String(length=20), nullable=False),
        sa.Column("image_url", sa.String(), nullable=False),
        sa.Column("pixabay_source_id", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("species_name", "growth_stage", "status_key", name="uq_pixabay_photo_cache_combo"),
    )
