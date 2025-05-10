"""add timestamps to user_plants

Revision ID: add_timestamps_to_user_plants
Revises: merge_heads
Create Date: 2024-05-10 12:55:06.787000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_timestamps_to_user_plants'
down_revision = 'merge_heads'
branch_labels = None
depends_on = None

def upgrade():
    # Check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user_plants')]
    
    if 'created_at' not in columns:
        op.add_column('user_plants', sa.Column('created_at', sa.DateTime(), nullable=True))
    
    if 'updated_at' not in columns:
        op.add_column('user_plants', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE user_plants SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP")
    
    # Make columns not nullable after setting defaults
    if 'created_at' not in columns:
        op.alter_column('user_plants', 'created_at', nullable=False)
    if 'updated_at' not in columns:
        op.alter_column('user_plants', 'updated_at', nullable=False)

def downgrade():
    # Check if columns exist before dropping them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user_plants')]
    
    if 'created_at' in columns:
        op.drop_column('user_plants', 'created_at')
    if 'updated_at' in columns:
        op.drop_column('user_plants', 'updated_at') 