"""check alembic version

Revision ID: check_alembic_version
Revises: fix_all_migrations
Create Date: 2024-05-10 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'check_alembic_version'
down_revision = 'fix_all_migrations'
branch_labels = None
depends_on = None

def upgrade():
    # First, let's see what's in the alembic_version table
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT * FROM alembic_version"))
    print("Current alembic_version table contents:")
    for row in result:
        print(row)
    
    # Now let's clean up any stale references
    conn.execute(sa.text("""
        DELETE FROM alembic_version 
        WHERE version_num IN ('merge_heads', 'add_timestamps_to_user_plants')
    """))
    
    # Ensure we have the correct version
    conn.execute(sa.text("""
        INSERT INTO alembic_version (version_num)
        VALUES ('fix_all_migrations')
        ON CONFLICT (version_num) DO NOTHING
    """))

def downgrade():
    pass 