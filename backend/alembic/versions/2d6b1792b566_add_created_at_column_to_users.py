"""Add created_at column to users

Revision ID: 2d6b1792b566
Revises: 5cf44b53f2ea
Create Date: 2025-05-07 12:12:25.238224

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2d6b1792b566'
down_revision: Union[str, None] = '5cf44b53f2ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'created_at')
