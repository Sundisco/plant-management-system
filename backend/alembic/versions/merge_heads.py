"""merge heads

Revision ID: merge_heads
Revises: 5acd350c893e, create_sections_table
Create Date: 2025-05-11 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_heads'
down_revision: Union[str, None] = ('5acd350c893e', 'create_sections_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass 