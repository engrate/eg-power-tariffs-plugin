"""Add Ellevio tariff definition

Revision ID: 52cb8eeee2d6
Revises: d1abcbd074b0
Create Date: 2025-05-22 10:58:46.350574+00:00

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ARRAY, UUID
from sqlalchemy.dialects.postgresql import JSONB

from engrate_sdk.utils.uuid import uuid7

# revision identifiers, used by Alembic.
revision: str = '52cb8eeee2d6'
down_revision: Union[str, None] = 'd1abcbd074b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ellevio_uuid = uuid7()
fee_uid = uuid7()

def upgrade() -> None:

    op.bulk_insert(
        sa.table(
            'providers',
            sa.column('uid', sa.Uuid),
            sa.column('name', sa.String),
            sa.column('org_number', sa.String),
            sa.column('ediel', sa.Integer),
            sa.column('active', sa.Boolean),
        ),
        [
            {'uid':ellevio_uuid,'name': 'Ellevio AB', 'org_number': '556037-7326', 'ediel': 14900, 'active': True},
        ],
    )


    # Parse datetime strings to datetime objects
    valid_from = datetime.strptime('01-01-2025', '%d-%m-%Y')
    valid_to = datetime.strptime('31-12-2025', '%d-%m-%Y')
    last_updated = datetime.now()

    # Generate UUIDs for power tariffs
    tariff_uid = uuid7()
    # Insert power_tariffs data
    op.bulk_insert(
        sa.table(
            'power_tariffs',
            sa.column('uid', UUID),
            sa.column('provider_uid', UUID),
            sa.column('country_code', sa.String),
            sa.column('time_zone', sa.String),
            sa.column('last_updated', sa.DateTime),
            sa.column('valid_from', sa.DateTime),
            sa.column('valid_to', sa.DateTime),
        ),
        [
            {
                'uid': tariff_uid,
                'provider_uid': ellevio_uuid,
                'country_code': 'SE',
                'time_zone': 'Europe/Stockholm',
                'last_updated': last_updated,
                'valid_from': valid_from,
                'valid_to': valid_to
            }
        ]
    )

    op.bulk_insert(
        sa.table(
            'power_tariff_fees',
            sa.column('uid', UUID),
            sa.column('tariff_id', UUID),
            sa.column('name', sa.String),
            sa.column('model', sa.String),
            sa.column('description', sa.Text),
            sa.column('samples_per_month', sa.Integer),
            sa.column('time_unit', sa.String),
            sa.column('building_types', ARRAY(sa.String)),
        ),
        [
            {
                'uid': fee_uid,
                'tariff_id': tariff_uid,
                'name': 'Standard fee',
                'model': 'avgMonthlyPeaks',
                'description': 'Average of the 3 highest power peaks (kW/h)',
                'samples_per_month': 3,
                'time_unit': 'hourly',
                'building_types': ['detached_house', 'terraced_house', 'summer_house']
            }
        ]
    )

    days =  ["M","T","W","T","F","S","S"]

    # Prepare intervals JSONB
    intervals = [
        {
            "from": "06:00",
            "to": "21:59",
            "multiplier": 1
        },
        {
            "from": "22:00",
            "to": "05:59",
            "multiplier": 0.5
        }
    ]

    op.bulk_insert(
        sa.table(
            'tariff_compositions',
            sa.column('uid', UUID),
            sa.column('fee_id', UUID),
            sa.column('months', ARRAY(sa.Integer)),
            sa.column('days', ARRAY(sa.String)),
            sa.column('fuse_from', sa.String),
            sa.column('fuse_to', sa.String),
            sa.column('hints', JSONB),
            sa.column('unit', sa.String),
            sa.column('price_exc_vat', sa.Float),
            sa.column('price_inc_vat', sa.Float),
            sa.column('intervals', JSONB),
        ),
        [
            {
                'uid': uuid7(),
                'fee_id': fee_uid,
                'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                'days': days,
                'fuse_from': '16A',
                'fuse_to': '63A',
                'hints': {'location': 'All regions'},  # Example hint
                'unit': 'kr/kw',
                'price_exc_vat': 65,
                'price_inc_vat': 81.25,
                'intervals': intervals
            }
        ]
    )

def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM providers WHERE uuid = :uuid CASCADE"),
        {'uuid': ellevio_uuid}
    )
