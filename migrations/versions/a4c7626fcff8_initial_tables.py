"""initial tables

Revision ID: a4c7626fcff8
Revises: 7a136a16c4f8
Create Date: 2025-07-01 00:37:16.781666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4c7626fcff8'
down_revision: Union[str, Sequence[str], None] = '7a136a16c4f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
