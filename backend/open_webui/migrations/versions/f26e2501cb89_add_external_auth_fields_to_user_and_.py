"""add external auth fields to user and auth tables with unique constraints

Revision ID: f26e2501cb89
Revises: 64ee58d1b4cf
Create Date: 2025-06-28 02:09:45.413080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'f26e2501cb89'
down_revision: Union[str, None] = '64ee58d1b4cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add unique constraints for auth table using batch operations
    with op.batch_alter_table('auth', schema=None) as batch_op:
        batch_op.create_unique_constraint('auth_external_user_id', ['external_user_id'])
        batch_op.create_unique_constraint('auth_phone', ['phone'])
    # Add unique constraints for user table using batch operations
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_unique_constraint('user_external_user_id', ['external_user_id'])
        batch_op.create_unique_constraint('user_phone', ['phone'])


def downgrade() -> None:
    # Remove unique constraints from user table using batch operations
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('user_phone', type_='unique')
        batch_op.drop_constraint('user_external_user_id', type_='unique')
    # Remove unique constraints from auth table using batch operations
    with op.batch_alter_table('auth', schema=None) as batch_op:
        batch_op.drop_constraint('auth_phone', type_='unique')
        batch_op.drop_constraint('auth_external_user_id', type_='unique')
