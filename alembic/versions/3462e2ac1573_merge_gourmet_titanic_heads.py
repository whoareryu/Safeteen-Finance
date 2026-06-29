"""merge gourmet/titanic heads

Revision ID: 3462e2ac1573
Revises: 20250604_0001, e7f8a9b0c1d2, f1a2b3c4d5e6
Create Date: 2026-06-28 22:27:39.894997

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3462e2ac1573'
down_revision: Union[str, Sequence[str], None] = ('20250604_0001', 'e7f8a9b0c1d2', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
