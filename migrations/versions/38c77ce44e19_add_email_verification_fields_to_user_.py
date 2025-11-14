"""Add email verification fields to User model

Revision ID: 38c77ce44e19
Revises: 759ba9649036
Create Date: 2025-11-15 01:19:04.129852

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38c77ce44e19'
down_revision: Union[str, Sequence[str], None] = '759ba9649036'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### ВИПРАВЛЕНО: Додаємо лише нові стовпці до існуючої таблиці 'user' ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_confirmed', sa.Boolean(), nullable=True, server_default=sa.false()))
        batch_op.add_column(sa.Column('email_confirmation_token', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### ВИПРАВЛЕНО: Видаляємо лише ці нові стовпці ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('email_confirmation_token')
        batch_op.drop_column('email_confirmed')
    # ### end Alembic commands ###