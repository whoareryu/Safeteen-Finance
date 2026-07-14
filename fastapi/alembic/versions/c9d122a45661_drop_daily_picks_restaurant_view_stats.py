"""drop daily_picks and restaurant_view_stats (orphaned after restaurants CASCADE drop)

Revision ID: c9d122a45661
Revises: 6b967960fd04
Create Date: 2026-07-14

"""

from typing import Sequence, Union

from alembic import op

revision: str = "c9d122a45661"
down_revision: Union[str, Sequence[str], None] = "6b967960fd04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = [
    "daily_picks",
    "restaurant_view_stats",
]


def upgrade() -> None:
    for table in _TABLES:
        op.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')


def downgrade() -> None:
    # Intentional no-op — see 6b967960fd04 for the documented precedent.
    pass
