from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_sections_table'
down_revision = 'add_search_indexes'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'sections',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('section_id', sa.String, nullable=False),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

def downgrade():
    op.drop_table('sections')
