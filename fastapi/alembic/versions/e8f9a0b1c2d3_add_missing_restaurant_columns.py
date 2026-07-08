"""add missing restaurant columns (biz_number, address, lat/lng)

Revision ID: e8f9a0b1c2d3
Revises: d2e3f4a5b6c7
Create Date: 2026-06-29
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "e8f9a0b1c2d3"
down_revision = "d2e3f4a5b6c7"
branch_labels = None
depends_on = None


def _has_column(inspector, table: str, column: str) -> bool:
    return any(c["name"] == column for c in inspector.get_columns(table))


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    text_cols = [
        ("biz_number",   sa.String(48), True),   # (name, type, unique)
        ("store_name",   sa.Text(),     False),
        ("branch_name",  sa.Text(),     False),
        ("road_address", sa.Text(),     False),
        ("parcel_address", sa.Text(),   False),
    ]
    for col_name, col_type, unique in text_cols:
        if not _has_column(insp, "restaurants", col_name):
            op.add_column(
                "restaurants",
                sa.Column(col_name, col_type, server_default="", nullable=False),
            )
            if unique:
                op.create_index(
                    f"ix_restaurants_{col_name}",
                    "restaurants",
                    [col_name],
                    unique=True,
                )

    float_cols = ["latitude", "longitude"]
    for col_name in float_cols:
        if not _has_column(insp, "restaurants", col_name):
            op.add_column(
                "restaurants",
                sa.Column(col_name, sa.Float(), nullable=True),
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    for col_name in ("latitude", "longitude", "parcel_address", "road_address",
                     "branch_name", "store_name", "biz_number"):
        if _has_column(insp, "restaurants", col_name):
            if col_name == "biz_number":
                op.drop_index("ix_restaurants_biz_number", table_name="restaurants")
            op.drop_column("restaurants", col_name)
