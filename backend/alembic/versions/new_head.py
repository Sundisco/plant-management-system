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
    # Add timestamp columns to user_plants table
    op.add_column('user_plants', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user_plants', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE user_plants SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP")
    
    # Make columns not nullable after setting defaults
    op.alter_column('user_plants', 'created_at', nullable=False)
    op.alter_column('user_plants', 'updated_at', nullable=False)

def downgrade():
    op.drop_column('user_plants', 'updated_at')
    op.drop_column('user_plants', 'created_at') 