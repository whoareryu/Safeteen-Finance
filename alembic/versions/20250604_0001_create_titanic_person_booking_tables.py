"""create titanic_persons and bookings

Revision ID: 20250604_0001
Revises:
Create Date: 2025-06-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20250604_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "titanic_persons",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("passenger_id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("gender", sa.String(length=16), nullable=False),
        sa.Column("age", sa.String(length=16), nullable=False),
        sa.Column("sib_sp", sa.String(length=16), nullable=False),
        sa.Column("parch", sa.String(length=16), nullable=False),
        sa.Column("survived", sa.String(length=8), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_titanic_persons_passenger_id"),
        "titanic_persons",
        ["passenger_id"],
        unique=False,
    )

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("person_id", sa.Integer(), nullable=False),
        sa.Column("pclass", sa.String(length=8), nullable=False),
        sa.Column("ticket", sa.String(length=128), nullable=False),
        sa.Column("fare", sa.String(length=64), nullable=False),
        sa.Column("cabin", sa.String(length=128), nullable=False),
        sa.Column("embarked", sa.String(length=8), nullable=False),
        sa.ForeignKeyConstraint(
            ["person_id"],
            ["titanic_persons.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_bookings_person_id"),
        "bookings",
        ["person_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_bookings_person_id"), table_name="bookings")
    op.drop_table("bookings")
    op.drop_index(op.f("ix_titanic_persons_passenger_id"), table_name="titanic_persons")
    op.drop_table("titanic_persons")
