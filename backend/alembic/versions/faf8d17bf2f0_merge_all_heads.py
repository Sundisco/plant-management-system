"""merge_all_heads

Revision ID: faf8d17bf2f0
Revises: add_search_indexes, merge_all_heads
Create Date: 2025-05-12 02:02:17.613863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'faf8d17bf2f0'
down_revision: Union[str, None] = ('add_search_indexes', 'merge_all_heads')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
