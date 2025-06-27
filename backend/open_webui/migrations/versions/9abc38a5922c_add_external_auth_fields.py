"""Add external auth fields

Revision ID: 9abc38a5922c
Revises: 9f0c9cd09105
Create Date: 2025-06-28 00:55:43.582326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '9abc38a5922c'
down_revision: Union[str, None] = '9f0c9cd09105'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # The columns already exist from previous migrations, so we only need to add constraints
    # Add unique constraints for the new fields (if they don't already exist)
    try:
        op.create_unique_constraint('uq_user_external_user_id', 'user', ['external_user_id'])
    except Exception:
        pass  # Constraint might already exist
    
    try:
        op.create_unique_constraint('uq_user_phone', 'user', ['phone'])
    except Exception:
        pass  # Constraint might already exist
    
    try:
        op.create_unique_constraint('uq_auth_external_user_id', 'auth', ['external_user_id'])
    except Exception:
        pass  # Constraint might already exist
    
    try:
        op.create_unique_constraint('uq_auth_phone', 'auth', ['phone'])
    except Exception:
        pass  # Constraint might already exist


def downgrade() -> None:
    # Drop unique constraints
    op.drop_constraint('uq_user_external_user_id', 'user', type_='unique')
    op.drop_constraint('uq_user_phone', 'user', type_='unique')
    op.drop_constraint('uq_auth_external_user_id', 'auth', type_='unique')
    op.drop_constraint('uq_auth_phone', 'auth', type_='unique')
    
    # Note: SQLite doesn't support dropping columns, so we can't remove them in downgrade
    # The columns will remain but won't be used
