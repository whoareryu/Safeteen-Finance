"""조회수(view_count) 제거 — restaurants.view_count 컬럼 drop (비스펙 대청소).

Revision ID: d2e3f4a5b6c7
Revises: c1f2a3d4b5e6
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, Sequence[str], None] = "c1f2a3d4b5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    insp = sa.inspect(op.get_bind())
    return any(c["name"] == column for c in insp.get_columns(table))


def upgrade() -> None:
    if _has_column("restaurants", "view_count"):
        op.drop_column("restaurants", "view_count")


def downgrade() -> None:
    if not _has_column("restaurants", "view_count"):
        op.add_column(
            "restaurants",
            sa.Column(
                "view_count",
                sa.Integer(),
                nullable=False,
                server_default="0",
            ),
        )
