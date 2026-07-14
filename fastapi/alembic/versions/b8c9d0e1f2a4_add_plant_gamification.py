"""add plant gamification — points/streak/growth_stage on plants, plant_checkins, plant_badges, user_plant_badges

Revision ID: b8c9d0e1f2a4
Revises: a7b8c9d0e1f2
Create Date: 2026-07-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b8c9d0e1f2a4"
down_revision: Union[str, Sequence[str], None] = "c9d0e1f2a4b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BADGES = [
    ("first_register", "첫 등록", "첫 반려식물을 등록했어요", "🌱"),
    ("first_checkin", "첫 출석체크", "첫 출석체크를 완료했어요", "📸"),
    ("streak_7", "7일 연속 출석", "7일 연속으로 출석체크했어요", "🔥"),
    ("streak_30", "30일 연속 출석", "30일 연속으로 출석체크했어요", "🏆"),
    ("growth_new_shoot", "새순 성장", "새순 단계로 성장했어요", "🌿"),
    ("growth_mature", "성목 달성", "성목 단계로 성장했어요", "🌳"),
]


def upgrade() -> None:
    op.add_column("plants", sa.Column("growth_stage", sa.String(length=10), nullable=False, server_default="새싹"))
    op.add_column("plants", sa.Column("points", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("plants", sa.Column("streak_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("plants", sa.Column("last_checkin_date", sa.Date(), nullable=True))
    op.alter_column("plants", "growth_stage", server_default=None)
    op.alter_column("plants", "points", server_default=None)
    op.alter_column("plants", "streak_count", server_default=None)

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
        [
            {"code": code, "name": name, "description": desc, "icon": icon}
            for code, name, desc, icon in _BADGES
        ],
    )


def downgrade() -> None:
    op.drop_table("user_plant_badges")
    op.drop_table("plant_badges")
    op.drop_table("plant_checkins")
    op.drop_column("plants", "last_checkin_date")
    op.drop_column("plants", "streak_count")
    op.drop_column("plants", "points")
    op.drop_column("plants", "growth_stage")
