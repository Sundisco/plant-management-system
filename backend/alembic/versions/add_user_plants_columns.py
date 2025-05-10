"""add user_plants columns

Revision ID: add_user_plants_columns
Revises: 
Create Date: 2024-05-10 11:57:19.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_plants_columns'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add created_at and updated_at columns
    op.add_column('user_plants', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('user_plants', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE user_plants SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP")
    
    # Make columns not nullable after setting defaults
    op.alter_column('user_plants', 'created_at', nullable=False)
    op.alter_column('user_plants', 'updated_at', nullable=False)

def downgrade():
    # Remove the columns
    op.drop_column('user_plants', 'created_at')
    op.drop_column('user_plants', 'updated_at') 