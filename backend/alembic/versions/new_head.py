"""new head

Revision ID: new_head
Revises: 5acd350c893e
Create Date: 2024-05-10 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'new_head'
down_revision = '5acd350c893e'  # Reference the last known good migration
branch_labels = None
depends_on = None

def upgrade():
    # Add section column to user_plants table if it doesn't exist
    op.add_column('user_plants', sa.Column('section', sa.String(), nullable=True))

def downgrade():
    op.drop_column('user_plants', 'section') 