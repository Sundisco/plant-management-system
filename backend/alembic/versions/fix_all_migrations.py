"""fix all migrations

Revision ID: fix_all_migrations
Revises: 14da059c1679
Create Date: 2024-05-10 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

## revision identifiers, used by Alembic.
revision = 'fix_all_migrations'
down_revision = '14da059c1679'  # Changed from 5acd350c893e to 14da059c1679
branch_labels = None
depends_on = None

def upgrade():
    # Add timestamps to user_plants if they don't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user_plants')]
    
    if 'created_at' not in columns:
        op.add_column('user_plants', sa.Column('created_at', sa.DateTime(), nullable=True))
        op.execute("UPDATE user_plants SET created_at = CURRENT_TIMESTAMP")
        op.alter_column('user_plants', 'created_at', nullable=False)
    
    if 'updated_at' not in columns:
        op.add_column('user_plants', sa.Column('updated_at', sa.DateTime(), nullable=True))
        op.execute("UPDATE user_plants SET updated_at = CURRENT_TIMESTAMP")
        op.alter_column('user_plants', 'updated_at', nullable=False)

    # Add missing watering schedule columns if they don't exist
    columns = [col['name'] for col in inspector.get_columns('watering_schedule')]
    if 'day' not in columns:
        op.add_column('watering_schedule', sa.Column('day', sa.String(), nullable=True))
    if 'amount' not in columns:
        op.add_column('watering_schedule', sa.Column('amount', sa.Float(), nullable=True))
    if 'weather_dependent' not in columns:
        op.add_column('watering_schedule', sa.Column('weather_dependent', sa.Boolean(), server_default='true', nullable=True))

    # Add created_at to users if it doesn't exist
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'created_at' not in columns:
        op.add_column('users', sa.Column('created_at', sa.DateTime(), nullable=True))
        op.execute("UPDATE users SET created_at = CURRENT_TIMESTAMP")
        op.alter_column('users', 'created_at', nullable=False)

def downgrade():
    # Remove timestamps from user_plants if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user_plants')]
    
    if 'created_at' in columns:
        op.drop_column('user_plants', 'created_at')
    if 'updated_at' in columns:
        op.drop_column('user_plants', 'updated_at')

    # Remove watering schedule columns if they exist
    columns = [col['name'] for col in inspector.get_columns('watering_schedule')]
    if 'day' in columns:
        op.drop_column('watering_schedule', 'day')
    if 'amount' in columns:
        op.drop_column('watering_schedule', 'amount')
    if 'weather_dependent' in columns:
        op.drop_column('watering_schedule', 'weather_dependent')

    # Remove created_at from users if it exists
    columns = [col['name'] for col in inspector.get_columns('users')]
    if 'created_at' in columns:
        op.drop_column('users', 'created_at') 