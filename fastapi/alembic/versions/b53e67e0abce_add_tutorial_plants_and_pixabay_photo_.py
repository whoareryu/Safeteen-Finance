"""add tutorial plants and pixabay photo cache

Revision ID: b53e67e0abce
Revises: d0e1f2a4b5c6
Create Date: 2026-07-17 16:34:44.682017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b53e67e0abce'
down_revision: Union[str, Sequence[str], None] = 'd0e1f2a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tutorial_plants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("species_name", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("growth_stage", sa.String(length=10), nullable=False, server_default="새싹"),
        sa.Column("soil_moisture_pct", sa.Float(), nullable=False, server_default="70"),
        sa.Column("nutrient_pct", sa.Float(), nullable=False, server_default="70"),
        sa.Column("light_position", sa.String(length=10), nullable=False, server_default="반양지"),
        sa.Column("points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_watered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_fertilized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_light_moved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_weather_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.alter_column("tutorial_plants", "growth_stage", server_default=None)
    op.alter_column("tutorial_plants", "soil_moisture_pct", server_default=None)
    op.alter_column("tutorial_plants", "nutrient_pct", server_default=None)
    op.alter_column("tutorial_plants", "light_position", server_default=None)
    op.alter_column("tutorial_plants", "points", server_default=None)
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


def downgrade() -> None:
    op.drop_table("pixabay_photo_caches")
    op.drop_index("ix_tutorial_plants_owner_user_id", table_name="tutorial_plants")
    op.drop_table("tutorial_plants")
