from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_glyph_to_sections'
down_revision = 'faf8d17bf2f0'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('sections', sa.Column('glyph', sa.String(), nullable=True))

def downgrade():
    op.drop_column('sections', 'glyph') 