"""fix migration chain

Revision ID: fix_migration_chain
Revises: 5acd350c893e
Create Date: 2024-05-10 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_migration_chain'
down_revision = '5acd350c893e'  # Reference the base migration
branch_labels = None
depends_on = None

def upgrade():
    # This migration is just to fix the chain
    # All necessary columns already exist in the base migration
    pass

def downgrade():
    # No downgrade needed as this is just a chain fix
    pass 