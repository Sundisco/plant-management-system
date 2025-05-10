"""add search indexes

Revision ID: add_search_indexes
Revises: fix_migration_chain
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_search_indexes'
down_revision = 'fix_migration_chain'
branch_labels = None
depends_on = None

def upgrade():
    # Add indexes for frequently searched columns
    op.create_index('ix_plants_common_name', 'plants', ['common_name'])
    op.create_index('ix_plants_type', 'plants', ['type'])
    
    # Create GIN indexes with array_ops operator class for array fields
    op.execute('CREATE INDEX ix_plants_scientific_name ON plants USING gin (scientific_name array_ops)')
    op.execute('CREATE INDEX ix_plants_other_names ON plants USING gin (other_names array_ops)')
    
    # Add indexes for user_plants table
    op.create_index('ix_user_plants_user_id', 'user_plants', ['user_id'])
    op.create_index('ix_user_plants_plant_id', 'user_plants', ['plant_id'])

def downgrade():
    # Remove indexes
    op.drop_index('ix_plants_common_name')
    op.drop_index('ix_plants_type')
    op.drop_index('ix_plants_scientific_name')
    op.drop_index('ix_plants_other_names')
    op.drop_index('ix_user_plants_user_id')
    op.drop_index('ix_user_plants_plant_id') 