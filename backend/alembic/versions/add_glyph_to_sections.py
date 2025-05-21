"""add glyph to sections

Revision ID: add_glyph_to_sections
Revises: faf8d17bf2f0
Create Date: 2024-05-16 14:56:20.066798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_glyph_to_sections'
down_revision: Union[str, None] = 'faf8d17bf2f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('sections', sa.Column('glyph', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('sections', 'glyph') 