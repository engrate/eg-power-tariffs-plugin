"""Add Tekniska Verken Linköping tariff definition

Revision ID: cf216217b707
Revises: d9bf73034df3
Create Date: 2025-05-26 10:16:32.227614+00:00

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import UUID, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from engrate_sdk.utils.uuid import uuid7

# revision identifiers, used by Alembic.
revision: str = 'cf216217b707'
down_revision: Union[str, None] = 'd9bf73034df3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


terken_uuid = uuid7()
default_fee_uid = uuid7()
alternative_fee_uid = uuid7()

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
            {'uid':terken_uuid,'name': u'Tekniska verken Linköping Nät AB', 'org_number': '556483-4926', 'ediel': 11900, 'active': True}
        ],
    )

    valid_from = datetime.strptime('01-01-2025', '%d-%m-%Y')
    valid_to = datetime.strptime('31-12-2025', '%d-%m-%Y')
    last_updated = datetime.now()
    tariff_uid = uuid7()

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
                'provider_uid': terken_uuid,
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
                'uid': default_fee_uid,
                'tariff_id': tariff_uid,
                'name': 'Default Standard fee',
                'model': 'avgMonthlyPeaks',
                'description': 'Average of the 5 monthly highest power peaks (kW/h)',
                'samples_per_month': 5,
                'time_unit': 'hourly',
                'building_types': ['detached_house', 'terraced_house', 'summer_house', 'apartments']
            },
            {
                'uid': alternative_fee_uid,
                'tariff_id': tariff_uid,
                'name': 'Alternative fee',
                'model': 'avgMonthlyPeaks',
                'description': 'Average of the 2 nightly and daily highest power peaks (kW/h)',
                'samples_per_month': 2,
                'time_unit': 'hourly',
                'building_types': ['detached_house', 'terraced_house', 'summer_house', 'apartments']
            }
        ]
    )

    default_compositions = [
        # Linköping Summer
        {
            'uid': uuid7(),
            'fee_id': default_fee_uid,
            'months': [4, 5, 6, 7, 8, 9, 10],
            'days': ['M','T','W','T','F','S','S'],
            'fuse_from': '16A',
            'fuse_to': '63A',
            'hints': [
                {"type": "geolocation", "value": "linköping"},
                {"type": "season", "value": "summer"}
            ],
            'unit': 'kr/kw',
            'price_exc_vat': 16.5,
            'price_inc_vat': 22,
            'intervals': [
                {
                    "from": "00:00",
                    "to": "23:59",
                    "multiplier": 1
                }
            ]
        },
        # Linköping Winter
        {
            'uid': uuid7(),
            'fee_id': default_fee_uid,
            'months': [1, 2, 3, 11, 12],
            'days':  ['M','T','W','T','F','S','S'],
            'fuse_from': '16A',
            'fuse_to': '63A',
            'hints': [
                {"type": "geolocation", "value": u"linköping"},
                {"type": "season", "value": "winter"}
            ],
            'unit': 'kr/kw',
            'price_exc_vat': 32.25,
            'price_inc_vat': 43,
            'intervals': [
                {
                    "from": "00:00",
                    "to": "23:59",
                    "multiplier": 1
                }
            ]
        }
    ]

    # Insert tariff_compositions data for Alternative fee
    alternative_compositions = [
        # Linköping Summer Day
        {
            'uid': uuid7(),
            'fee_id': alternative_fee_uid,
            'months': [4, 5, 6, 7, 8, 9, 10],
            'days': ['M','T','W','T','F','S','S'],
            'fuse_from': '16A',
            'fuse_to': '63A',
            'hints': [
                {"type": "geolocation", "value": u"linköping"},
                {"type": "season", "value": "summer"},
                {"type": "timeOfDay", "value": "day"}
            ],
            'unit': 'kr/kw',
            'price_exc_vat': 16.5,
            'price_inc_vat': 22,
            'intervals': [
                {
                    "from": "06:00",
                    "to": "23:00",
                    "multiplier": 1
                }
            ]
        },
        # Linköping Summer Night
        {
            'uid': uuid7(),
            'fee_id': alternative_fee_uid,
            'months': [4, 5, 6, 7, 8, 9, 10],
            'days': ['M','T','W','T','F','S','S'],
            'fuse_from': '16A',
            'fuse_to': '63A',
            'hints': [
                {"type": "geolocation", "value": u"linköping"},
                {"type": "season", "value": "summer"},
                {"type": "timeOfDay", "value": "night"}
            ],
            'unit': 'kr/kw',
            'price_exc_vat': 6,
            'price_inc_vat': 8,
            'intervals': [
                {
                    "from": "23:01",
                    "to": "05:59",
                    "multiplier": 1
                }
            ]
        },
        # Linköping Winter Day
        {
            'uid': uuid7(),
            'fee_id': alternative_fee_uid,
            'months': [1, 2, 3, 11, 12],
            'days': ['M','T','W','T','F','S','S'],
            'fuse_from': '16A',
            'fuse_to': '63A',
            'hints': [
                {"type": "geolocation", "value": u"linköping"},
                {"type": "season", "value": "winter"},
                {"type": "timeOfDay", "value": "day"}
            ],
            'unit': 'kr/kw',
            'price_exc_vat': 32.25,
            'price_inc_vat': 43,
            'intervals': [
                {
                    "from": "06:00",
                    "to": "23:00",
                    "multiplier": 1
                }
            ]
        },
        # Linköping Winter Night
        {
            'uid': uuid7(),
            'fee_id': alternative_fee_uid,
            'months': [1, 2, 3, 11, 12],
            'days': ['M','T','W','T','F','S','S'],
            'fuse_from': '16A',
            'fuse_to': '63A',
            'hints': [
                {"type": "geolocation", "value": u"linköping"},
                {"type": "season", "value": "winter"},
                {"type": "timeOfDay", "value": "night"}
            ],
            'unit': 'kr/kw',
            'price_exc_vat': 9,
            'price_inc_vat': 12,
            'intervals': [
                {
                    "from": "23:01",
                    "to": "05:59",
                    "multiplier": 1
                }
            ]
        }
    ]

    # Combine all compositions and insert them
    all_compositions = default_compositions + alternative_compositions

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
        all_compositions
    )



def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM providers WHERE uuid = :uuid CASCADE"),
        {'uuid': terken_uuid}
    )

