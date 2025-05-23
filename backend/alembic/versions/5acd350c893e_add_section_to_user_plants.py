"""add section to user_plants

Revision ID: 5acd350c893e
Revises: 
Create Date: 2025-04-14 13:44:39.102715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5acd350c893e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.drop_table('watering_log')
    op.drop_table('weather_forecast')
    op.drop_index('idx_attracts_plant_id', table_name='attracts')
    op.drop_index('idx_attracts_species', table_name='attracts')
    op.create_index(op.f('ix_attracts_id'), 'attracts', ['id'], unique=False)
    op.drop_index('idx_plant_guides_plant_id', table_name='plant_guides')
    op.drop_index('idx_plant_guides_type', table_name='plant_guides')
    op.create_index(op.f('ix_plant_guides_id'), 'plant_guides', ['id'], unique=False)
    op.alter_column('plants', 'common_name',
               existing_type=sa.TEXT(),
               nullable=True)
    op.alter_column('plants', 'is_evergreen',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.alter_column('plants', 'edible_fruit',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.drop_index('idx_common_name', table_name='plants')
    op.drop_index('idx_plants_growth_rate_maintenance', table_name='plants')
    op.drop_index('idx_scientific_name', table_name='plants', postgresql_using='gin')
    op.create_index(op.f('ix_plants_id'), 'plants', ['id'], unique=False)
    op.drop_index('idx_plant_id_pruning', table_name='pruning')
    op.drop_index('idx_pruning_frequency', table_name='pruning')
    op.drop_index('idx_pruning_plant_id', table_name='pruning')
    op.create_index(op.f('ix_pruning_id'), 'pruning', ['id'], unique=False)
    op.drop_index('idx_plant_id_sunlight', table_name='sunlight')
    op.drop_index('idx_sunlight_condition', table_name='sunlight')
    op.drop_index('idx_sunlight_plant_id', table_name='sunlight')
    op.create_index(op.f('ix_sunlight_id'), 'sunlight', ['id'], unique=False)
    op.add_column('user_plants', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('user_plants', sa.Column('section', sa.String(), nullable=True))
    op.alter_column('user_plants', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('user_plants', 'plant_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_index(op.f('ix_user_plants_id'), 'user_plants', ['id'], unique=False)
    op.create_foreign_key(None, 'user_plants', 'users', ['user_id'], ['id'])
    op.drop_index('idx_plant_id_watering', table_name='watering')
    op.drop_index('idx_watering_frequency_days', table_name='watering')
    op.drop_index('idx_watering_plant_id', table_name='watering')
    op.create_index(op.f('ix_watering_id'), 'watering', ['id'], unique=False)
    op.create_index(op.f('ix_watering_schedules_id'), 'watering_schedules', ['id'], unique=False)
    op.create_foreign_key(None, 'watering_schedules', 'plants', ['plant_id'], ['id'])
    op.create_foreign_key(None, 'watering_schedules', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'watering_schedules', type_='foreignkey')
    op.drop_constraint(None, 'watering_schedules', type_='foreignkey')
    op.drop_index(op.f('ix_watering_schedules_id'), table_name='watering_schedules')
    op.drop_index(op.f('ix_watering_id'), table_name='watering')
    op.create_index('idx_watering_plant_id', 'watering', ['plant_id'], unique=False)
    op.create_index('idx_watering_frequency_days', 'watering', ['frequency_days'], unique=False)
    op.create_index('idx_plant_id_watering', 'watering', ['plant_id'], unique=False)
    op.drop_constraint(None, 'user_plants', type_='foreignkey')
    op.drop_index(op.f('ix_user_plants_id'), table_name='user_plants')
    op.alter_column('user_plants', 'plant_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('user_plants', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('user_plants', 'section')
    op.drop_column('user_plants', 'id')
    op.drop_index(op.f('ix_sunlight_id'), table_name='sunlight')
    op.create_index('idx_sunlight_plant_id', 'sunlight', ['plant_id'], unique=False)
    op.create_index('idx_sunlight_condition', 'sunlight', ['condition'], unique=False)
    op.create_index('idx_plant_id_sunlight', 'sunlight', ['plant_id'], unique=False)
    op.drop_index(op.f('ix_pruning_id'), table_name='pruning')
    op.create_index('idx_pruning_plant_id', 'pruning', ['plant_id'], unique=False)
    op.create_index('idx_pruning_frequency', 'pruning', ['frequency'], unique=False)
    op.create_index('idx_plant_id_pruning', 'pruning', ['plant_id'], unique=False)
    op.drop_index(op.f('ix_plants_id'), table_name='plants')
    op.create_index('idx_scientific_name', 'plants', ['scientific_name'], unique=False, postgresql_using='gin')
    op.create_index('idx_plants_growth_rate_maintenance', 'plants', ['growth_rate', 'maintenance'], unique=False)
    op.create_index('idx_common_name', 'plants', ['common_name'], unique=False)
    op.alter_column('plants', 'edible_fruit',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.alter_column('plants', 'is_evergreen',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    op.alter_column('plants', 'common_name',
               existing_type=sa.TEXT(),
               nullable=False)
    op.drop_index(op.f('ix_plant_guides_id'), table_name='plant_guides')
    op.create_index('idx_plant_guides_type', 'plant_guides', ['type'], unique=False)
    op.create_index('idx_plant_guides_plant_id', 'plant_guides', ['plant_id'], unique=False)
    op.drop_index(op.f('ix_attracts_id'), table_name='attracts')
    op.create_index('idx_attracts_species', 'attracts', ['species'], unique=False)
    op.create_index('idx_attracts_plant_id', 'attracts', ['plant_id'], unique=False)
    op.create_table('weather_forecast',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('timestamp', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('location', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('temperature', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('precipitation', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('wind_speed', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='weather_forecast_pkey'),
    sa.UniqueConstraint('timestamp', 'location', name='unique_weather')
    )
    op.create_table('watering_log',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('plant_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('decision_date', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
    sa.Column('water_needed', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('reason', sa.TEXT(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['plant_id'], ['plants.id'], name='watering_log_plant_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='watering_log_pkey')
    )
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
