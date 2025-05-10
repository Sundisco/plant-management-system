"""merge heads final

Revision ID: merge_heads_final
Revises: 14da059c1679, fix_all_migrations
Create Date: 2024-05-10 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_heads_final'
down_revision = ('14da059c1679', 'fix_all_migrations')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 