"""migrate sections

Revision ID: migrate_sections
Revises: merge_heads
Create Date: 2025-05-11 12:10:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision: str = 'migrate_sections'
down_revision: Union[str, None] = 'merge_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add unique constraint on user_id and section_id
    op.create_unique_constraint(
        'uq_sections_user_section',
        'sections',
        ['user_id', 'section_id']
    )

    # Get all unique sections from user_plants
    conn = op.get_bind()
    result = conn.execute(text("""
        SELECT DISTINCT user_id, section 
        FROM user_plants 
        WHERE section IS NOT NULL
    """))
    
    # Create sections for each unique combination
    for row in result:
        user_id, section_id = row
        # Generate a name based on the section_id
        name = f"Section {section_id}"
        
        # Insert into sections table
        conn.execute(text("""
            INSERT INTO sections (user_id, section_id, name)
            VALUES (:user_id, :section_id, :name)
            ON CONFLICT (user_id, section_id) DO NOTHING
        """), {
            'user_id': user_id,
            'section_id': section_id,
            'name': name
        })


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_sections_user_section', 'sections', type_='unique') 