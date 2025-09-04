"""Initial PowerTariff schema

Revision ID: 9824b55b6d3b
Revises: 
Create Date: 2025-05-21 12:17:26.018984+00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import UUID, ARRAY, JSON

# revision identifiers, used by Alembic.
revision: str = '9824b55b6d3b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Create grid_operators table
    op.create_table(
        'grid_operators',
        sa.Column('uid', UUID, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("ediel", sa.Integer(), nullable=False),
        sa.UniqueConstraint("ediel"),
        sa.UniqueConstraint('name'),
    )

    op.create_index(
        'ix_grid_operators_name',
        'grid_operators', ['name'],
    )

    op.create_index(
        'ix_grid_operators_ediel',
        'grid_operators', ['ediel'],
    )

    # Create metering_grid_areas table
    op.create_table(
        'metering_grid_areas',
        sa.Column("code", sa.String(length=5), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False, server_default='SE'),
        sa.Column("metering_business_area", sa.String(length=5), nullable=False),
        sa.Column('grid_operator_uid', UUID, nullable=False),
        sa.UniqueConstraint('name'),
    )

    op.create_foreign_key(
        'fk_metering_grid_areas_grid_operator_uid',
        'metering_grid_areas', 'grid_operators',
        ['grid_operator_uid'], ['uid'],
    )

    op.create_index(
        'ix_metering_grid_areas_grid_operator_uid',
        'metering_grid_areas', ['grid_operator_uid'],
    )

    # Create power_tariffs table (must be created before the junction table)
    op.create_table(
        'power_tariffs',
        sa.Column('uid', UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('samples_per_month', sa.Integer(), nullable=False),
        sa.Column('time_unit', sa.String(length=20), nullable=False),
        sa.Column('building_type', sa.String(length=50), nullable=False, server_default='All'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_to', sa.DateTime(timezone=True), nullable=False),
        sa.Column('compositions', JSON, nullable=False),
    )

    # Create junction table for many-to-many relationship
    op.create_table(
        'metering_grid_area_x_power_tariff',
        sa.Column("uid", sa.UUID, primary_key=True),
        sa.Column("mga_code", sa.String(length=5), nullable=False),
        sa.Column("tariff_uid", UUID, nullable=False),
        sa.Column("voltage", sa.String(length=10), nullable=False),
    )

    op.create_foreign_key(
        "fk_mgas_x_tariffs_mga_code",
        "metering_grid_area_x_power_tariff",
        "metering_grid_areas",
        ["mga_code"],
        ["code"]
    )

    op.create_foreign_key(
        "fk_mgas_x_tariffs_tariff_uid",
        "metering_grid_area_x_power_tariff",
        "power_tariffs",
        ["tariff_uid"],
        ["uid"]
    )

    # Create indexes for the junction table
    op.create_index(
        'ix_metering_grid_area_x_power_tariff_mga_code',
        'metering_grid_area_x_power_tariff', ['mga_code'],
    )

    op.create_index(
        'ix_metering_grid_area_x_power_tariff_tariff_uid',
        'metering_grid_area_x_power_tariff', ['tariff_uid'],
    )

    # Create composite index for better query performance
    op.create_index(
        'ix_metering_grid_area_x_power_tariff_mga_tariff',
        'metering_grid_area_x_power_tariff', ['mga_code', 'tariff_uid'],
        unique=True  # Ensure no duplicate relationships
    )


def downgrade():
    # Drop indexes first
    op.drop_index('ix_metering_grid_area_x_power_tariff_mga_tariff')
    op.drop_index('ix_metering_grid_area_x_power_tariff_tariff_uid')
    op.drop_index('ix_metering_grid_area_x_power_tariff_mga_code')
    op.drop_index('ix_metering_grid_areas_grid_operator_uid')
    op.drop_index('ix_grid_operators_ediel')
    op.drop_index('ix_grid_operators_name')

    # Drop foreign key constraints
    op.drop_constraint('fk_mgas_x_tariffs_tariff_uid', 'metering_grid_area_x_power_tariff')
    op.drop_constraint('fk_mgas_x_tariffs_mga_code', 'metering_grid_area_x_power_tariff')
    op.drop_constraint('fk_metering_grid_areas_grid_operator_uid', 'metering_grid_areas')

    # Drop tables in reverse order
    op.drop_table('metering_grid_area_x_power_tariff')
    op.drop_table('power_tariffs')
    op.drop_table('metering_grid_areas')
    op.drop_table('grid_operators')
