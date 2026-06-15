"""normalize gourmet 3NF: sigungu, biz_class, tags, contact, hours

Revision ID: b1c2d3e4f5a6
Revises: f8a9b0c1d2e3
Create Date: 2026-05-22

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "f8a9b0c1d2e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(inspector, table: str, column: str) -> bool:
    return column in {c["name"] for c in inspector.get_columns(table)}


def _has_table(inspector, table: str) -> bool:
    return inspector.has_table(table)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not _has_table(inspector, "sigungu_districts"):
        op.create_table(
            "sigungu_districts",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("sigungu_name", sa.String(32), server_default="", nullable=False),
            sa.Column("district_label", sa.String(128), server_default="", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "sigungu_name", "district_label", name="uq_sigungu_districts_name_label"
            ),
        )
        op.create_index(
            "ix_sigungu_districts_district_label",
            "sigungu_districts",
            ["district_label"],
        )

    if not _has_table(inspector, "biz_classifications"):
        op.create_table(
            "biz_classifications",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("biz_mid_name", sa.String(64), server_default="", nullable=False),
            sa.Column("biz_minor_name", sa.String(128), server_default="", nullable=False),
            sa.Column("ksic_name", sa.String(256), server_default="", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "biz_mid_name",
                "biz_minor_name",
                "ksic_name",
                name="uq_biz_classifications_triple",
            ),
        )
        op.create_index(
            "ix_biz_classifications_ksic", "biz_classifications", ["ksic_name"]
        )

    if not _has_table(inspector, "tags"):
        op.create_table(
            "tags",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("slug", sa.String(64), nullable=False),
            sa.Column("label", sa.String(128), server_default="", nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("slug"),
        )
        op.create_index("ix_tags_slug", "tags", ["slug"], unique=True)

    if not _has_table(inspector, "restaurant_tags"):
        op.create_table(
            "restaurant_tags",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("restaurant_id", sa.Integer(), nullable=False),
            sa.Column("tag_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "restaurant_id", "tag_id", name="uq_restaurant_tags_pair"
            ),
        )
        op.create_index("ix_restaurant_tags_restaurant_id", "restaurant_tags", ["restaurant_id"])
        op.create_index("ix_restaurant_tags_tag_id", "restaurant_tags", ["tag_id"])

    if not _has_table(inspector, "restaurant_contacts"):
        op.create_table(
            "restaurant_contacts",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("restaurant_id", sa.Integer(), nullable=False),
            sa.Column("phone", sa.String(32), nullable=True),
            sa.Column("place_url", sa.String(512), nullable=True),
            sa.Column("source_note", sa.Text(), server_default="", nullable=False),
            sa.ForeignKeyConstraint(["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("restaurant_id"),
        )
        op.create_index(
            "ix_restaurant_contacts_restaurant_id",
            "restaurant_contacts",
            ["restaurant_id"],
            unique=True,
        )

    if not _has_table(inspector, "restaurant_operating_hours"):
        op.create_table(
            "restaurant_operating_hours",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("restaurant_id", sa.Integer(), nullable=False),
            sa.Column("weekday", sa.Integer(), nullable=False),
            sa.Column("open_time", sa.String(8), nullable=True),
            sa.Column("close_time", sa.String(8), nullable=True),
            sa.Column("is_closed", sa.Boolean(), server_default="false", nullable=False),
            sa.Column("note", sa.String(256), server_default="", nullable=False),
            sa.ForeignKeyConstraint(["restaurant_id"], ["restaurant.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "restaurant_id", "weekday", name="uq_restaurant_operating_hours_day"
            ),
        )
        op.create_index(
            "ix_restaurant_operating_hours_restaurant_id",
            "restaurant_operating_hours",
            ["restaurant_id"],
        )

    inspector = sa.inspect(bind)
    if _has_column(inspector, "restaurants", "district"):
        op.execute(
            """
            INSERT INTO sigungu_districts (sigungu_name, district_label)
            SELECT DISTINCT
                COALESCE(NULLIF(TRIM(sigungu_name), ''), '미상'),
                COALESCE(NULLIF(TRIM(district), ''), '미상')
            FROM restaurants
            ON CONFLICT ON CONSTRAINT uq_sigungu_districts_name_label DO NOTHING
            """
        )
        op.execute(
            """
            INSERT INTO biz_classifications (biz_mid_name, biz_minor_name, ksic_name)
            SELECT DISTINCT
                COALESCE(TRIM(biz_mid_name), ''),
                COALESCE(TRIM(biz_minor_name), ''),
                COALESCE(TRIM(ksic_name), '')
            FROM restaurants
            ON CONFLICT ON CONSTRAINT uq_biz_classifications_triple DO NOTHING
            """
        )

    inspector = sa.inspect(bind)
    if not _has_column(inspector, "restaurants", "sigungu_id"):
        op.add_column(
            "restaurants",
            sa.Column("sigungu_id", sa.Integer(), nullable=True),
        )
    if not _has_column(inspector, "restaurants", "biz_classification_id"):
        op.add_column(
            "restaurants",
            sa.Column("biz_classification_id", sa.Integer(), nullable=True),
        )

    if _has_column(inspector, "restaurants", "district"):
        op.execute(
            """
            UPDATE restaurants r
            SET sigungu_id = s.id
            FROM sigungu_districts s
            WHERE COALESCE(NULLIF(TRIM(r.sigungu_name), ''), '미상') = s.sigungu_name
              AND COALESCE(NULLIF(TRIM(r.district), ''), '미상') = s.district_label
            """
        )
        op.execute(
            """
            UPDATE restaurants r
            SET biz_classification_id = b.id
            FROM biz_classifications b
            WHERE COALESCE(TRIM(r.biz_mid_name), '') = b.biz_mid_name
              AND COALESCE(TRIM(r.biz_minor_name), '') = b.biz_minor_name
              AND COALESCE(TRIM(r.ksic_name), '') = b.ksic_name
            """
        )

        default_sigungu = bind.execute(
            sa.text(
                "INSERT INTO sigungu_districts (sigungu_name, district_label) "
                "VALUES ('미상', '미상') "
                "ON CONFLICT ON CONSTRAINT uq_sigungu_districts_name_label DO NOTHING "
                "RETURNING id"
            )
        ).scalar()
        if default_sigungu is None:
            default_sigungu = bind.execute(
                sa.text(
                    "SELECT id FROM sigungu_districts "
                    "WHERE sigungu_name='미상' AND district_label='미상'"
                )
            ).scalar()
        default_biz = bind.execute(
            sa.text(
                "INSERT INTO biz_classifications (biz_mid_name, biz_minor_name, ksic_name) "
                "VALUES ('', '', '') "
                "ON CONFLICT ON CONSTRAINT uq_biz_classifications_triple DO NOTHING "
                "RETURNING id"
            )
        ).scalar()
        if default_biz is None:
            default_biz = bind.execute(
                sa.text(
                    "SELECT id FROM biz_classifications "
                    "WHERE biz_mid_name='' AND biz_minor_name='' AND ksic_name=''"
                )
            ).scalar()

        op.execute(
            sa.text(
                "UPDATE restaurants SET sigungu_id = :sid WHERE sigungu_id IS NULL"
            ).bindparams(sid=default_sigungu)
        )
        op.execute(
            sa.text(
                "UPDATE restaurants SET biz_classification_id = :bid "
                "WHERE biz_classification_id IS NULL"
            ).bindparams(bid=default_biz)
        )

        inspector = sa.inspect(bind)
        if _has_column(inspector, "restaurants", "ai_tags"):
            op.execute(
                """
                INSERT INTO tags (slug, label)
                SELECT DISTINCT
                    SUBSTRING(MD5(TRIM(elem)) FROM 1 FOR 32),
                    LEFT(TRIM(elem), 128)
                FROM restaurants r,
                     LATERAL jsonb_array_elements_text(
                         CASE
                             WHEN jsonb_typeof(r.ai_tags) = 'array' THEN r.ai_tags
                             ELSE '[]'::jsonb
                         END
                     ) AS elem
                WHERE TRIM(elem) <> ''
                ON CONFLICT (slug) DO NOTHING
                """
            )
            op.execute(
                """
                INSERT INTO restaurant_tags (restaurant_id, tag_id)
                SELECT DISTINCT r.id, t.id
                FROM restaurants r,
                     LATERAL jsonb_array_elements_text(
                         CASE
                             WHEN jsonb_typeof(r.ai_tags) = 'array' THEN r.ai_tags
                             ELSE '[]'::jsonb
                         END
                     ) AS elem
                JOIN tags t ON t.label = LEFT(TRIM(elem), 128)
                WHERE TRIM(elem) <> ''
                ON CONFLICT ON CONSTRAINT uq_restaurant_tags_pair DO NOTHING
                """
            )

        for idx in (
            "ix_restaurants_category_district_id",
            "ix_restaurants_district",
            "ix_restaurants_category_id",
            "ix_restaurants_category_price_id",
            "ix_restaurants_category_slug",
            "ix_restaurants_avg_price",
        ):
            op.execute(sa.text(f'DROP INDEX IF EXISTS "{idx}"'))

        fk_names = {
            fk["name"] for fk in sa.inspect(bind).get_foreign_keys("restaurants")
        }
        if "fk_restaurants_sigungu_id" not in fk_names:
            op.create_foreign_key(
            "fk_restaurants_sigungu_id",
            "restaurants",
            "sigungu_districts",
            ["sigungu_id"],
            ["id"],
            ondelete="RESTRICT",
            )
        if "fk_restaurants_biz_classification_id" not in fk_names:
            op.create_foreign_key(
            "fk_restaurants_biz_classification_id",
            "restaurants",
            "biz_classifications",
            ["biz_classification_id"],
            ["id"],
            ondelete="RESTRICT",
            )
        op.alter_column("restaurants", "sigungu_id", nullable=False)
        op.alter_column("restaurants", "biz_classification_id", nullable=False)

        op.drop_column("restaurants", "district")
        op.drop_column("restaurants", "sigungu_name")
        op.drop_column("restaurants", "biz_mid_name")
        op.drop_column("restaurants", "biz_minor_name")
        op.drop_column("restaurants", "ksic_name")
        if _has_column(sa.inspect(bind), "restaurants", "ai_tags"):
            op.drop_column("restaurants", "ai_tags")

        op.create_index(
            "ix_restaurants_category_sigungu_id",
            "restaurants",
            ["category_id", "sigungu_id", "id"],
        )
        op.create_index("ix_restaurants_sigungu_id", "restaurants", ["sigungu_id"])
        op.create_index(
            "ix_restaurants_biz_classification_id",
            "restaurants",
            ["biz_classification_id"],
        )


def downgrade() -> None:
    pass
