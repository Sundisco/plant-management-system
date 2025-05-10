"""reset migrations

Revision ID: reset_migrations
Revises: 
Create Date: 2024-05-10 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'reset_migrations'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Drop and recreate the alembic_version table
    op.execute("DROP TABLE IF EXISTS alembic_version")
    op.execute("""
        CREATE TABLE alembic_version (
            version_num VARCHAR(32) NOT NULL,
            CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
        )
    """)
    
    # Insert our base migration
    op.execute("INSERT INTO alembic_version (version_num) VALUES ('5acd350c893e')")

def downgrade():
    pass 