"""add watering fields to plants

Revision ID: add_watering_fields
Revises: 5cf44b53f2ea
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_watering_fields'
down_revision = '5cf44b53f2ea'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to plants table
    op.add_column('plants', sa.Column('watering_frequency_days', sa.Integer(), nullable=True))
    op.add_column('plants', sa.Column('watering_depth_mm', sa.Integer(), nullable=True))
    op.add_column('plants', sa.Column('watering_volume_feet', sa.Float(), nullable=True))
    op.add_column('plants', sa.Column('watering_period', sa.Text(), nullable=True))
    op.add_column('plants', sa.Column('drought_tolerant', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('plants', sa.Column('soil_requirements', postgresql.ARRAY(sa.Text()), nullable=True))

def downgrade():
    # Remove columns from plants table
    op.drop_column('plants', 'soil_requirements')
    op.drop_column('plants', 'drought_tolerant')
    op.drop_column('plants', 'watering_period')
    op.drop_column('plants', 'watering_volume_feet')
    op.drop_column('plants', 'watering_depth_mm')
    op.drop_column('plants', 'watering_frequency_days') 