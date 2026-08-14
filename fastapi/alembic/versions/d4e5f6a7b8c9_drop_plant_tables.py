"""drop plant tables — apps/plant(새싹) 백엔드 제거에 따른 정리 (SafeTeen Finance 마이그레이션)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-08-11

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PLANT_KNOWLEDGE_EMBEDDING_DIM = 1024

_BADGES = [
    ("first_register", "첫 등록", "첫 반려식물을 등록했어요", "🌱"),
    ("first_checkin", "첫 출석체크", "첫 출석체크를 완료했어요", "📸"),
    ("streak_7", "7일 연속 출석", "7일 연속으로 출석체크했어요", "🔥"),
    ("streak_30", "30일 연속 출석", "30일 연속으로 출석체크했어요", "🏆"),
    ("growth_new_shoot", "새순 성장", "새순 단계로 성장했어요", "🌿"),
    ("growth_mature", "성목 달성", "성목 단계로 성장했어요", "🌳"),
]


def upgrade() -> None:
    op.drop_table("user_plant_badges")
    op.drop_table("plant_badges")
    op.drop_table("plant_checkins")
    op.drop_table("care_prescriptions")
    op.drop_table("diagnosis_records")
    op.drop_table("care_schedules")
    op.drop_table("notification_events")
    op.drop_index("ix_weather_snapshots_region", table_name="weather_snapshots")
    op.drop_table("weather_snapshots")
    op.drop_table("plants")
    op.drop_table("plant_knowledge_images")
    op.drop_table("plant_knowledge")


def downgrade() -> None:
    op.create_table(
        "plant_knowledge",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(PLANT_KNOWLEDGE_EMBEDDING_DIM), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "plant_knowledge_images",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("knowledge_id", sa.Integer(), nullable=False),
        sa.Column("image_filename", sa.String(), nullable=False),
        sa.Column("split", sa.String(length=10), nullable=True),
        sa.Column("bbox_x_center", sa.Float(), nullable=True),
        sa.Column("bbox_y_center", sa.Float(), nullable=True),
        sa.Column("bbox_width", sa.Float(), nullable=True),
        sa.Column("bbox_height", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["knowledge_id"], ["plant_knowledge.id"]),
    )

    op.create_table(
        "plants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("nickname", sa.String(), nullable=False),
        sa.Column("species_name", sa.String(), nullable=False),
        sa.Column("region", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("growth_stage", sa.String(length=10), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("streak_count", sa.Integer(), nullable=False),
        sa.Column("last_checkin_date", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
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

    op.create_table(
        "notification_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=True),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("coupang_link", sa.String(), nullable=True),
        sa.Column("triggered_by", sa.String(), nullable=False),
        sa.Column("delivery_status", sa.String(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
    )
    op.create_table(
        "care_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
        sa.Column("last_watered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_watering_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
    )
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
    op.create_table(
        "plant_checkins",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("photo_url", sa.String(), nullable=False),
        sa.Column("checkin_date", sa.Date(), nullable=False),
        sa.Column("health_score", sa.Float(), nullable=False),
        sa.Column("points_earned", sa.Integer(), nullable=False),
        sa.Column("streak_day", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
    )
    op.create_table(
        "plant_badges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=40), nullable=False),
        sa.Column("description", sa.String(length=120), nullable=False),
        sa.Column("icon", sa.String(length=10), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_table(
        "user_plant_badges",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("badge_id", sa.Integer(), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        sa.ForeignKeyConstraint(["badge_id"], ["plant_badges.id"]),
    )

    badges_table = sa.table(
        "plant_badges",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("icon", sa.String),
    )
    op.bulk_insert(
        badges_table,
        [{"code": code, "name": name, "description": desc, "icon": icon} for code, name, desc, icon in _BADGES],
    )
