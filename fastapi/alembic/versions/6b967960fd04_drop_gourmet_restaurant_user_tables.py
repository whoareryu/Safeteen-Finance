"""drop gourmet/restaurant/user tables (plant manager 마이그레이션)

Revision ID: 6b967960fd04
Revises: e8f9a0b1c2d3
Create Date: 2026-07-13
"""
from __future__ import annotations

from alembic import op

revision = "6b967960fd04"
down_revision = "e8f9a0b1c2d3"
branch_labels = None
depends_on = None

# FK로 서로 참조하지만 CASCADE로 삭제하므로 순서에 안전하다.
_TABLES = [
    "restaurant_tags",
    "restaurant_prices",
    "restaurant_operating_hours",
    "restaurant_menus",
    "restaurant_contacts",
    "daily_recommendations",
    "meal_plan_expenses",
    "meal_plans",
    "restaurant_visits",
    "user_preferences",
    "search_query_logs",
    "restaurants",
    "food_categories",
    "sigungu_districts",
    "biz_classifications",
    "tags",
]


def upgrade() -> None:
    for table in _TABLES:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')


def downgrade() -> None:
    # gourmetmate(restaurant/user) 도메인은 plant 매니저로 완전히 대체되었으므로
    # downgrade에서 테이블을 복구하지 않는다 (3462e2ac1573 선례와 동일한 no-op).
    pass
