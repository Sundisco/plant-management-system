"""fix migration chain final

Revision ID: fix_migration_chain_final
Revises: e5a31c7256df
Create Date: 2024-05-10 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_migration_chain_final'
down_revision = 'e5a31c7256df'  # This is the last working migration
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

def downgrade():
    # Remove timestamps from user_plants if they exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user_plants')]
    
    if 'created_at' in columns:
        op.drop_column('user_plants', 'created_at')
    if 'updated_at' in columns:
        op.drop_column('user_plants', 'updated_at') 