"""merge all heads

Revision ID: merge_all_heads
Revises: merge_heads, migrate_sections
Create Date: 2025-05-11 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'merge_all_heads'
down_revision: Union[str, None] = ('merge_heads', 'migrate_sections')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass 