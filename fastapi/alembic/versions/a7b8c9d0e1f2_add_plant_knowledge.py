"""add plant_knowledge, plant_knowledge_images — RAG 지식베이스 (PlantDoc + house_plant_species)

Revision ID: a7b8c9d0e1f2
Revises: f3a4b5c6d7e8
Create Date: 2026-07-14

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f3a4b5c6d7e8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PLANT_KNOWLEDGE_EMBEDDING_DIM = 1024


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

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


def downgrade() -> None:
    op.drop_table("plant_knowledge_images")
    op.drop_table("plant_knowledge")
