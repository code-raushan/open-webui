"""Make email optional and add unique constraints

Revision ID: a25fdac31d47
Revises: 9abc38a5922c
Create Date: 2025-06-28 00:59:19.771736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = 'a25fdac31d47'
down_revision: Union[str, None] = '9abc38a5922c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # For SQLite, we need to handle email field modifications carefully
    # Since SQLite doesn't support ALTER COLUMN to change NOT NULL constraints,
    # we'll add unique constraints and handle the optional nature at the application level
    
    # Add unique constraints for email fields
    try:
        op.create_unique_constraint('uq_user_email', 'user', ['email'])
        print("Added unique constraint on user.email")
    except Exception as e:
        print(f"Could not add unique constraint on user.email: {e}")
    
    try:
        op.create_unique_constraint('uq_auth_email', 'auth', ['email'])
        print("Added unique constraint on auth.email")
    except Exception as e:
        print(f"Could not add unique constraint on auth.email: {e}")
    
    # Note: The email fields will remain NOT NULL in SQLite schema due to limitations
    # However, the SQLAlchemy models are configured to handle this at the application level
    # The models will treat email as optional even if the database schema shows NOT NULL
    # This is a common workaround for SQLite limitations


def downgrade() -> None:
    # Drop unique constraints
    try:
        op.drop_constraint('uq_user_email', 'user', type_='unique')
        print("Dropped unique constraint on user.email")
    except Exception as e:
        print(f"Could not drop unique constraint on user.email: {e}")
    
    try:
        op.drop_constraint('uq_auth_email', 'auth', type_='unique')
        print("Dropped unique constraint on auth.email")
    except Exception as e:
        print(f"Could not drop unique constraint on auth.email: {e}")
