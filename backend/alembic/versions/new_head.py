"""new head

Revision ID: new_head
Revises: fix_all_migrations
Create Date: 2024-05-10 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'new_head'
down_revision = 'fix_all_migrations'
branch_labels = None
depends_on = None

def upgrade():
    # This migration is just to establish a new head
    pass

def downgrade():
    pass 