"""add telegram_messages — n8n을 거치지 않는 Telegram Bot API 직접 발송 이력

Revision ID: d0e1f2a4b5c6
Revises: b8c9d0e1f2a4
Create Date: 2026-07-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d0e1f2a4b5c6"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "telegram_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("telegram_messages")
