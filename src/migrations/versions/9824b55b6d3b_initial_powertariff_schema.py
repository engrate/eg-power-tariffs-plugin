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
    # Create the power_tariff schema
    op.execute('CREATE SCHEMA IF NOT EXISTS power_tariffs')

    # Create providers table
    op.create_table(
        'providers',
        sa.Column('uid', UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("org_number", sa.String(length=50), nullable=True),
        sa.Column("ediel",sa.Integer(),nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default='true'),
        sa.UniqueConstraint("ediel"),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint("org_number"),
        schema= "power_tariffs"
    )

    op.create_index(
        'ix_providers_name',
        'providers', ['name'],
        schema='power_tariffs'
    )

    op.create_index(
        'ix_providers_org_number',
        'providers', ['org_number'],
        schema='power_tariffs'
    )

    op.create_index(
        'ix_providers_ediel',
        'providers', ['ediel'],
        schema='power_tariffs'
    )

    # Create power_tariffs table
    op.create_table(
        'power_tariffs',
        sa.Column('uid', UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('provider_uid', UUID, nullable=False),
        sa.Column("country_code", sa.String(length=2), nullable=False),
        sa.Column("time_zone", sa.String(length=50), nullable=False, server_default='Europe/Stockholm'),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_to', sa.DateTime(timezone=True), nullable=False),
        schema='power_tariffs'
    )

    op.create_foreign_key(
        'fk_power_tariffs_provider_uid',
        'power_tariffs', 'providers',
        ['provider_uid'], ['uid'],
        source_schema='power_tariffs', referent_schema='power_tariffs'
    )

    # Create power_tariff_fees table
    op.create_table(
        'power_tariff_fees',
        sa.Column('uid', UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('tariff_id', UUID, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('model', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('samples_per_month', sa.Integer(), nullable=False),
        sa.Column('time_unit', sa.String(length=20), nullable=False),
        sa.Column('building_types', ARRAY(sa.String(length=50))),
        schema='power_tariffs'
    )

    op.create_foreign_key(
        'fk_power_tariff_fees_tariff_id',
        'power_tariff_fees', 'power_tariffs',
        ['tariff_id'], ['uid'],
        source_schema='power_tariffs', referent_schema='power_tariffs',
        ondelete='CASCADE'
    )
    op.create_index(
        'ix_power_tariff_fees_tariff_id',
        'power_tariff_fees', ['tariff_id'],
        schema='power_tariffs'
    )

    # Create tariff_compositions table
    op.create_table(
        'tariff_compositions',
        sa.Column('uid', UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('fee_id', UUID, nullable=False),
        sa.Column('months', ARRAY(sa.Integer()), nullable=False),
        sa.Column('days', ARRAY(sa.String()), nullable=False),
        sa.Column('fuse_from', sa.String(length=10), nullable=False),
        sa.Column('fuse_to', sa.String(length=10), nullable=False),
        sa.Column('hints', JSON),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('price_exc_vat', sa.Float(), nullable=False),
        sa.Column('price_inc_vat', sa.Float(), nullable=False),
        sa.Column('intervals', JSON, nullable=False),
        schema='power_tariffs'
    )

    # Add foreign key constraint separately
    op.create_foreign_key(
        'fk_tariff_compositions_fee_id',
        'tariff_compositions', 'power_tariff_fees',
        ['fee_id'], ['uid'],
        source_schema='power_tariffs', referent_schema='power_tariffs',
        ondelete='CASCADE'
    )
    op.create_index(
        'ix_tariff_compositions_fee_id',
        'tariff_compositions', ['fee_id'],
        schema='power_tariffs'
    )

def downgrade():
    # Drop foreign key constraints first
    op.drop_constraint(
        'fk_tariff_compositions_fee_id', 'tariff_compositions',
        schema='power_tariffs'
    )
    op.drop_constraint(
        'fk_power_tariff_fees_tariff_id', 'power_tariff_fees',
        schema='power_tariffs'
    )

    # Drop tables in reverse order
    op.drop_index('ix_tariff_compositions_fee_id', schema='power_tariffs')
    op.drop_table('tariff_compositions', schema='power_tariffs')

    op.drop_index('ix_power_tariff_fees_tariff_id', schema='power_tariffs')
    op.drop_table('power_tariff_fees', schema='power_tariffs')

    op.drop_table('power_tariffs', schema='power_tariffs')

    # Drop the schema
    op.execute('DROP SCHEMA power_tariffs')
