"""merge watering heads final

Revision ID: merge_watering_heads_final
Revises: add_missing_watering_columns, add_watering_fields
Create Date: 2024-03-19 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'merge_watering_heads_final'
down_revision = ('add_missing_watering_columns', 'add_watering_fields')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass 