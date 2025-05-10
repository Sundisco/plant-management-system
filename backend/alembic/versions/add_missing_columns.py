"""add missing columns

Revision ID: add_missing_columns
Revises: add_timestamps_to_user_plants
Create Date: 2024-05-10 14:26:56.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_missing_columns'
down_revision = 'add_timestamps_to_user_plants'
branch_labels = None
depends_on = None

def upgrade():
    # Check if columns exist before adding them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check and add columns to user_plants table
    user_plants_columns = [col['name'] for col in inspector.get_columns('user_plants')]
    if 'created_at' not in user_plants_columns:
        op.add_column('user_plants', sa.Column('created_at', sa.DateTime(), nullable=True))
    if 'updated_at' not in user_plants_columns:
        op.add_column('user_plants', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Check and add columns to users table
    users_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'is_active' not in users_columns:
        op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    if 'created_at' not in users_columns:
        op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
    if 'updated_at' not in users_columns:
        op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE user_plants SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP")
    op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP, is_active = true")
    
    # Make columns not nullable after setting defaults
    if 'created_at' not in user_plants_columns:
        op.alter_column('user_plants', 'created_at', nullable=False)
    if 'updated_at' not in user_plants_columns:
        op.alter_column('user_plants', 'updated_at', nullable=False)
    if 'created_at' not in users_columns:
        op.alter_column('users', 'created_at', nullable=False)
    if 'updated_at' not in users_columns:
        op.alter_column('users', 'updated_at', nullable=False)
    if 'is_active' not in users_columns:
        op.alter_column('users', 'is_active', nullable=False)

def downgrade():
    # Check if columns exist before dropping them
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check and drop columns from user_plants table
    user_plants_columns = [col['name'] for col in inspector.get_columns('user_plants')]
    if 'created_at' in user_plants_columns:
        op.drop_column('user_plants', 'created_at')
    if 'updated_at' in user_plants_columns:
        op.drop_column('user_plants', 'updated_at')
    
    # Check and drop columns from users table
    users_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'is_active' in users_columns:
        op.drop_column('users', 'is_active')
    if 'created_at' in users_columns:
        op.drop_column('users', 'created_at')
    if 'updated_at' in users_columns:
        op.drop_column('users', 'updated_at') 