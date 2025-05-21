"""Add weather_adjusted column to watering_schedules table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_weather_adjusted'
down_revision = 'add_glyph_to_sections'  # Point to the current migration
branch_labels = None
depends_on = None

def upgrade():
    # Add weather_adjusted column
    op.add_column('watering_schedules',
        sa.Column('weather_adjusted', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade():
    # Remove weather_adjusted column
    op.drop_column('watering_schedules', 'weather_adjusted') 