"""create plant core tables — plants, diagnosis_records, care_prescriptions, care_schedules, notification_events, weather_snapshots

이 6개 테이블은 apps/plant 최초 도입 시 AUTO_CREATE_TABLES(암묵적 create_all)에만
의존하고 alembic 마이그레이션으로 정식 생성된 적이 없었다. 이후 마이그레이션에서
plants를 ALTER하려면 먼저 존재를 보장해야 하므로 여기서 idempotent하게 생성한다.

Revision ID: c9d0e1f2a4b5
Revises: a7b8c9d0e1f2
Create Date: 2026-07-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d0e1f2a4b5"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    if not _has_table("plants"):
        op.create_table(
            "plants",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("owner_user_id", sa.Integer(), nullable=True),
            sa.Column("nickname", sa.String(), nullable=False),
            sa.Column("species_name", sa.String(), nullable=False),
            sa.Column("region", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("diagnosis_records"):
        op.create_table(
            "diagnosis_records",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("plant_id", sa.Integer(), nullable=False),
            sa.Column("photo_url", sa.String(), nullable=False),
            sa.Column("detected_species", sa.String(), nullable=False),
            sa.Column("species_confidence", sa.Float(), nullable=False),
            sa.Column("symptom_label", sa.String(), nullable=False),
            sa.Column("symptom_confidence", sa.Float(), nullable=False),
            sa.Column("diagnosed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        )

    if not _has_table("care_prescriptions"):
        op.create_table(
            "care_prescriptions",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("diagnosis_record_id", sa.Integer(), nullable=False),
            sa.Column("prescription_text", sa.Text(), nullable=False),
            sa.Column("llm_model", sa.String(), nullable=False),
            sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["diagnosis_record_id"], ["diagnosis_records.id"]),
        )

    if not _has_table("care_schedules"):
        op.create_table(
            "care_schedules",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("plant_id", sa.Integer(), nullable=False),
            sa.Column("interval_days", sa.Integer(), nullable=False),
            sa.Column("last_watered_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("next_watering_due_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("status", sa.String(), nullable=False, server_default="active"),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        )
        op.alter_column("care_schedules", "status", server_default=None)

    if not _has_table("notification_events"):
        op.create_table(
            "notification_events",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("plant_id", sa.Integer(), nullable=True),
            sa.Column("channel", sa.String(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("coupang_link", sa.String(), nullable=True),
            sa.Column("triggered_by", sa.String(), nullable=False),
            sa.Column("delivery_status", sa.String(), nullable=False, server_default="pending"),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        )
        op.alter_column("notification_events", "delivery_status", server_default=None)

    if not _has_table("weather_snapshots"):
        op.create_table(
            "weather_snapshots",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("region", sa.String(), nullable=False),
            sa.Column("temp_c", sa.Float(), nullable=False),
            sa.Column("humidity_pct", sa.Float(), nullable=False),
            sa.Column("sunlight_desc", sa.String(), nullable=False),
            sa.Column("is_dry_day", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.alter_column("weather_snapshots", "is_dry_day", server_default=None)
        op.create_index("ix_weather_snapshots_region", "weather_snapshots", ["region"])


def downgrade() -> None:
    for table in (
        "notification_events",
        "care_schedules",
        "care_prescriptions",
        "diagnosis_records",
        "weather_snapshots",
        "plants",
    ):
        if _has_table(table):
            op.drop_table(table)
