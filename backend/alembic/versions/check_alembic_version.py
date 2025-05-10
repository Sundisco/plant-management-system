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
    # Print the contents of alembic_version table
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT * FROM alembic_version"))
    print("Current alembic_version table contents:")
    for row in result:
        print(row)

def downgrade():
    pass 