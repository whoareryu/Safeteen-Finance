"""add region to users

Revision ID: 1fb74f4c3118
Revises: b53e67e0abce
Create Date: 2026-07-17 16:48:59.809479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fb74f4c3118'
down_revision: Union[str, Sequence[str], None] = 'b53e67e0abce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("region", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "region")
