"""add missing external auth fields to user and auth tables

Revision ID: 64ee58d1b4cf
Revises: 8caa931f21d1
Create Date: 2025-06-28 02:05:46.071280

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '64ee58d1b4cf'
down_revision: Union[str, None] = '8caa931f21d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing external auth fields to user table using batch operations
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('external_user_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('auth_provider', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove columns from user table
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('auth_provider')
        batch_op.drop_column('phone')
        batch_op.drop_column('external_user_id')
