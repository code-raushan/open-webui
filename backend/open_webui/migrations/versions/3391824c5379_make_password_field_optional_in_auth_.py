"""Make password field optional in auth table

Revision ID: 3391824c5379
Revises: 155967e47f55
Create Date: 2025-06-28 01:14:17.798145

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db


# revision identifiers, used by Alembic.
revision: str = '3391824c5379'
down_revision: Union[str, None] = '155967e47f55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch operations for SQLite to make password field optional
    with op.batch_alter_table('auth', schema=None) as batch_op:
        # Modify password column to be nullable (optional)
        batch_op.alter_column('password',
                             existing_type=sa.Text(),
                             nullable=True)


def downgrade() -> None:
    # Use batch operations for SQLite to make password field required again
    with op.batch_alter_table('auth', schema=None) as batch_op:
        # Modify password column to be not nullable (required)
        batch_op.alter_column('password',
                             existing_type=sa.Text(),
                             nullable=False)
