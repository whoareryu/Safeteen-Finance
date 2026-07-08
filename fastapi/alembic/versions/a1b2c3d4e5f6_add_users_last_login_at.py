"""legacy: last_login_at / role (handled in 44fda02bbdb4 or merge migration)

Revision ID: a1b2c3d4e5f6
Revises: 44fda02bbdb4
Create Date: 2026-05-19

"""

from typing import Sequence, Union

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "44fda02bbdb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
