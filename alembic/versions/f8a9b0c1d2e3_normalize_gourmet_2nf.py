"""normalize restaurants: food_categories, restaurant_prices, restaurant_menus

Revision ID: f8a9b0c1d2e3
Revises: e7f8a9b0c1d2
Create Date: 2026-05-21

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f8a9b0c1d2e3"
down_revision: Union[str, Sequence[str], None] = "d0e1f2a3b4c5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_CATEGORY_SEED = [
    ("hansik", "한식"),
    ("ilsik", "일식"),
    ("jungsik", "중식"),
    ("yangsik", "양식"),
    ("asian", "아시안"),
    ("bunsik", "분식"),
    ("cafe-dessert", "카페·디저트"),
    ("bar", "바"),
]


def _has_column(inspector, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspector.get_columns(table)}


def _has_index(inspector, table: str, index_name: str) -> bool:
    return index_name in {i["name"] for i in inspector.get_indexes(table)}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("food_categories"):
        op.create_table(
            "food_categories",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("slug", sa.String(length=32), nullable=False),
            sa.Column("label", sa.String(length=32), server_default="", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_food_categories_slug", "food_categories", ["slug"], unique=True)

    for slug, label in _CATEGORY_SEED:
        op.execute(
            sa.text(
                "INSERT INTO food_categories (slug, label) "
                "SELECT :slug, :label WHERE NOT EXISTS "
                "(SELECT 1 FROM food_categories WHERE slug = :slug)"
            ).bindparams(slug=slug, label=label)
        )

    if not inspector.has_table("restaurant_prices"):
        op.create_table(
            "restaurant_prices",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("restaurant_id", sa.Integer(), nullable=False),
            sa.Column("avg_price", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("restaurant_id", name="uq_restaurant_prices_restaurant_id"),
        )
        op.create_index(
            "ix_restaurant_prices_restaurant_id", "restaurant_prices", ["restaurant_id"]
        )
        op.create_index(
            "ix_restaurant_prices_avg_price", "restaurant_prices", ["avg_price"]
        )

    if not inspector.has_table("restaurant_menus"):
        op.create_table(
            "restaurant_menus",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("restaurant_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=256), server_default="", nullable=False),
            sa.Column("is_signature", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
            sa.Column("unit_price", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_restaurant_menus_restaurant_id", "restaurant_menus", ["restaurant_id"]
        )

    inspector = sa.inspect(bind)
    if _has_column(inspector, "restaurants", "category_slug"):
        if not _has_column(inspector, "restaurants", "category_id"):
            op.add_column(
                "restaurants",
                sa.Column("category_id", sa.Integer(), nullable=True),
            )

        op.execute(
            """
            UPDATE restaurants r
            SET category_id = c.id
            FROM food_categories c
            WHERE r.category_slug = c.slug
            """
        )
        op.execute(
            """
            UPDATE restaurants
            SET category_id = (SELECT id FROM food_categories WHERE slug = 'hansik')
            WHERE category_id IS NULL
            """
        )

        op.execute(
            """
            INSERT INTO restaurant_prices (restaurant_id, avg_price)
            SELECT r.id, r.avg_price FROM restaurants r
            WHERE r.avg_price IS NOT NULL
              AND NOT EXISTS (
                SELECT 1 FROM restaurant_prices p WHERE p.restaurant_id = r.id
              )
            """
        )
        op.execute(
            """
            INSERT INTO restaurant_menus (restaurant_id, name, is_signature, sort_order)
            SELECT id, signature_menu, true, 0 FROM restaurants
            WHERE COALESCE(TRIM(signature_menu), '') <> ''
            """
        )

        op.alter_column("restaurants", "category_id", nullable=False)
        inspector = sa.inspect(bind)
        fk_names = {fk["name"] for fk in inspector.get_foreign_keys("restaurants")}
        if "fk_restaurants_category_id" not in fk_names:
            op.create_foreign_key(
                "fk_restaurants_category_id",
                "restaurants",
                "food_categories",
                ["category_id"],
                ["id"],
                ondelete="RESTRICT",
            )
        if not _has_index(inspector, "restaurants", "ix_restaurants_category_id"):
            op.create_index(
                "ix_restaurants_category_id", "restaurants", ["category_id", "id"]
            )

        for idx in (
            "ix_restaurants_category_district_id",
            "ix_restaurants_category_price_id",
            "ix_restaurants_category_slug",
        ):
            try:
                op.drop_index(idx, table_name="restaurants")
            except Exception:
                pass

        op.drop_column("restaurants", "category_slug")
        op.drop_column("restaurants", "category_label")
        op.drop_column("restaurants", "avg_price")
        op.drop_column("restaurants", "signature_menu")

        inspector = sa.inspect(bind)
        if not _has_index(inspector, "restaurants", "ix_restaurants_category_district_id"):
            op.create_index(
                "ix_restaurants_category_district_id",
                "restaurants",
                ["category_id", "district", "id"],
            )


def downgrade() -> None:
    pass
