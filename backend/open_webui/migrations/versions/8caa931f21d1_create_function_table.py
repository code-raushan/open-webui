"""create function table

Revision ID: 8caa931f21d1
Revises: 3391824c5379
Create Date: 2025-06-28 01:59:09.722366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import open_webui.internal.db
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = '8caa931f21d1'
down_revision: Union[str, None] = '3391824c5379'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'function',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String()),
        sa.Column('name', sa.Text()),
        sa.Column('type', sa.Text()),
        sa.Column('content', sa.Text()),
        sa.Column('meta', open_webui.internal.db.JSONField()),
        sa.Column('valves', open_webui.internal.db.JSONField()),
        sa.Column('is_active', sa.Boolean()),
        sa.Column('is_global', sa.Boolean()),
        sa.Column('updated_at', sa.BigInteger()),
        sa.Column('created_at', sa.BigInteger()),
    )


def downgrade() -> None:
    op.drop_table('function')
