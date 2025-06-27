"""Batch operations for email optionality and unique constraints

Revision ID: 155967e47f55
Revises: a25fdac31d47
Create Date: 2025-06-28 01:00:52.880607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '155967e47f55'
down_revision: Union[str, None] = 'a25fdac31d47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite to properly modify table schemas
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Drop existing indexes first (with error handling)
        try:
            batch_op.drop_index('user_api_key')
        except:
            pass
        try:
            batch_op.drop_index('user_id')
        except:
            pass
        try:
            batch_op.drop_index('user_oauth_sub')
        except:
            pass
        
        # Modify email column to be nullable (optional)
        batch_op.alter_column('email',
                             existing_type=sa.VARCHAR(length=255),
                             nullable=True)
        
        # Recreate indexes and add unique constraints
        batch_op.create_unique_constraint('user_id', ['id'])
        batch_op.create_unique_constraint('user_api_key', ['api_key'])
        batch_op.create_unique_constraint('user_oauth_sub', ['oauth_sub'])
        batch_op.create_unique_constraint('user_email', ['email'])
        batch_op.create_unique_constraint('user_external_user_id', ['external_user_id'])
        batch_op.create_unique_constraint('user_phone', ['phone'])

    with op.batch_alter_table('auth', schema=None) as batch_op:
        # Drop existing index first (with error handling)
        try:
            batch_op.drop_index('auth_id')
        except:
            pass
        
        # Modify email column to be nullable (optional)
        batch_op.alter_column('email',
                             existing_type=sa.VARCHAR(length=255),
                             nullable=True)
        
        # Recreate index and add unique constraints
        batch_op.create_unique_constraint('auth_id', ['id'])
        batch_op.create_unique_constraint('auth_email', ['email'])
        batch_op.create_unique_constraint('auth_external_user_id', ['external_user_id'])
        batch_op.create_unique_constraint('auth_phone', ['phone'])


def downgrade() -> None:
    # Reverse the changes
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Drop unique constraints
        batch_op.drop_constraint('user_email', type_='unique')
        batch_op.drop_constraint('user_external_user_id', type_='unique')
        batch_op.drop_constraint('user_phone', type_='unique')
        
        # Drop indexes
        batch_op.drop_index('user_id')
        batch_op.drop_index('user_api_key')
        batch_op.drop_index('user_oauth_sub')
        
        # Make email NOT NULL again
        batch_op.alter_column('email',
                             existing_type=sa.VARCHAR(length=255),
                             nullable=False)
        
        # Recreate original indexes
        batch_op.create_unique_constraint('user_id', ['id'])
        batch_op.create_unique_constraint('user_api_key', ['api_key'])
        batch_op.create_unique_constraint('user_oauth_sub', ['oauth_sub'])

    with op.batch_alter_table('auth', schema=None) as batch_op:
        # Drop unique constraints
        batch_op.drop_constraint('auth_email', type_='unique')
        batch_op.drop_constraint('auth_external_user_id', type_='unique')
        batch_op.drop_constraint('auth_phone', type_='unique')
        
        # Drop index
        batch_op.drop_index('auth_id')
        
        # Make email NOT NULL again
        batch_op.alter_column('email',
                             existing_type=sa.VARCHAR(length=255),
                             nullable=False)
        
        # Recreate original index
        batch_op.create_unique_constraint('auth_id', ['id'])
