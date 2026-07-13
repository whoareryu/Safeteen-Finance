"""create soccer schema: stadium, team, schedule, player (+ pgvector)

Revision ID: a4b5c6d7e8f9
Revises: e8f9a0b1c2d3
Create Date: 2026-07-13

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "a4b5c6d7e8f9"
down_revision: Union[str, Sequence[str], None] = "e8f9a0b1c2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PLAYER_EMBEDDING_DIM = 1536


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    if not _has_table("stadium"):
        op.create_table(
            "stadium",
            sa.Column("stadium_id", sa.String(length=10), nullable=False),
            sa.Column("statdium_name", sa.String(length=40), nullable=False),
            sa.Column("hometeam_id", sa.String(length=10), nullable=True),
            sa.Column("seat_count", sa.Integer(), nullable=True),
            sa.Column("address", sa.String(length=60), nullable=True),
            sa.Column("ddd", sa.String(length=10), nullable=True),
            sa.Column("tel", sa.String(length=10), nullable=True),
            sa.PrimaryKeyConstraint("stadium_id"),
        )

    if not _has_table("team"):
        op.create_table(
            "team",
            sa.Column("team_id", sa.String(length=10), nullable=False),
            sa.Column("region_name", sa.String(length=10), nullable=False),
            sa.Column("team_name", sa.String(length=40), nullable=False),
            sa.Column("e_team_name", sa.String(length=50), nullable=True),
            sa.Column("orig_yyyy", sa.String(length=10), nullable=True),
            sa.Column("zip_code1", sa.String(length=10), nullable=True),
            sa.Column("zip_code2", sa.String(length=10), nullable=True),
            sa.Column("address", sa.String(length=80), nullable=True),
            sa.Column("ddd", sa.String(length=10), nullable=True),
            sa.Column("tel", sa.String(length=10), nullable=True),
            sa.Column("fax", sa.String(length=10), nullable=True),
            sa.Column("homepage", sa.String(length=50), nullable=True),
            sa.Column("owner", sa.String(length=10), nullable=True),
            sa.Column("stadium_id", sa.String(length=10), nullable=True),
            sa.PrimaryKeyConstraint("team_id"),
            sa.ForeignKeyConstraint(["stadium_id"], ["stadium.stadium_id"]),
        )

    if not _has_table("schedule"):
        op.create_table(
            "schedule",
            sa.Column("sche_date", sa.String(length=10), nullable=False),
            sa.Column("stadium_id", sa.String(length=10), nullable=False),
            sa.Column("gubun", sa.String(length=10), nullable=True),
            sa.Column("hometeam_id", sa.String(length=10), nullable=True),
            sa.Column("awayteam_id", sa.String(length=10), nullable=True),
            sa.Column("home_score", sa.Integer(), nullable=True),
            sa.Column("away_score", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("sche_date", "stadium_id"),
            sa.ForeignKeyConstraint(["stadium_id"], ["stadium.stadium_id"]),
        )

    if not _has_table("player"):
        op.create_table(
            "player",
            sa.Column("player_id", sa.String(length=10), nullable=False),
            sa.Column("player_name", sa.String(length=20), nullable=False),
            sa.Column("e_player_name", sa.String(length=40), nullable=True),
            sa.Column("nickname", sa.String(length=30), nullable=True),
            sa.Column("join_yyyy", sa.String(length=10), nullable=True),
            sa.Column("position", sa.String(length=10), nullable=True),
            sa.Column("back_no", sa.Integer(), nullable=True),
            sa.Column("nation", sa.String(length=20), nullable=True),
            sa.Column("birth_date", sa.Date(), nullable=True),
            sa.Column("solar", sa.String(length=10), nullable=True),
            sa.Column("height", sa.Integer(), nullable=True),
            sa.Column("weight", sa.Integer(), nullable=True),
            sa.Column("team_id", sa.String(length=10), nullable=True),
            sa.Column("player_embedding", Vector(PLAYER_EMBEDDING_DIM), nullable=True),
            sa.PrimaryKeyConstraint("player_id"),
            sa.ForeignKeyConstraint(["team_id"], ["team.team_id"]),
        )


def downgrade() -> None:
    for table in ("player", "schedule", "team", "stadium"):
        if _has_table(table):
            op.drop_table(table)
