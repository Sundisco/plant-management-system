"""add missing watering schedule columns

Revision ID: add_missing_watering_columns
Revises: 5cf44b53f2ea
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_missing_watering_columns'
down_revision = '5cf44b53f2ea'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('watering_schedule', sa.Column('day', sa.String(), nullable=True))
    op.add_column('watering_schedule', sa.Column('amount', sa.Float(), nullable=True))
    op.add_column('watering_schedule', sa.Column('weather_dependent', sa.Boolean(), server_default='true', nullable=True))

def downgrade():
    # Remove columns
    op.drop_column('watering_schedule', 'day')
    op.drop_column('watering_schedule', 'amount')
    op.drop_column('watering_schedule', 'weather_dependent') 