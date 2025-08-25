"""Add Malaren tariff definition

Revision ID: d1abcbd074b0
Revises: 9824b55b6d3b
Create Date: 2025-05-22 08:28:58.623852+00:00

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import UUID, ARRAY
from sqlalchemy.dialects.postgresql import JSONB

from engrate_sdk.utils.uuid import uuid7

# revision identifiers, used by Alembic.
revision: str = 'd1abcbd074b0'
down_revision: Union[str, None] = '9824b55b6d3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

### Generate UUIDs for providers
malaren_uuid= uuid7()


def upgrade() -> None:
    op.bulk_insert(
        sa.table(
            'providers',
            sa.column('uid', sa.Uuid),
            sa.column('name', sa.String),
            sa.column('org_number', sa.String),
            sa.column('ediel', sa.Integer),
            sa.column('active', sa.Boolean),
            schema = 'power_tariffs'
        ),
        [
            {'uid':malaren_uuid,'name': u'Mälarenergi Elnät AB', 'org_number': '556448-9150', 'ediel': 39300, 'active': True}
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
            schema='power_tariffs'
        ),
        [
            {
                'uid': tariff_uid,
                'provider_uid': malaren_uuid,
                'country_code': 'SE',
                'time_zone': 'Europe/Stockholm',
                'last_updated': last_updated,
                'valid_from': valid_from,
                'valid_to': valid_to
            }
        ]
    )
    fee_uid = uuid7()
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
            schema='power_tariffs'
        ),
        [
            {
                'uid': fee_uid,
                'tariff_id': tariff_uid,
                'name': 'Monthly - One single peak',
                'model': 'avgMonthlyPeaks',
                'description': 'Monthly single peak (kW/h)',
                'samples_per_month': 1,
                'time_unit': 'hourly',
                'building_types': ['detached_house', 'terraced_house', 'summer_house', 'apartments']
            }
        ]
    )
    intervals = [
        {
            "from": "07:00",
            "to": "19:00",
            "multiplier": 1
        }
    ]

    hints = [
        {"type": "geolocation", "value": u"Barkarö"},
        {"type": "geolocation", "value": u"Enhagen-Ekbacken"},
        {"type": "geolocation", "value": u"Gångholmen och Tidö-Lindö"},
        {"type": "season", "value": "summer"},
        {"type": "dayRestriction", "value": "non-holydays"}
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
            schema='power_tariffs'
        ),
        [
            {
                'uid': uuid7(),
                'fee_id': fee_uid,
                'months': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                'days': ['M','T','W','T','F'],
                'fuse_from': '16A',
                'fuse_to': '63A',
                'hints': hints,
                'unit': 'kr/kw',
                'price_exc_vat': 14.06,
                'price_inc_vat': 18.75,
                'intervals': intervals
            }
        ]
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM power_tariffs.providers WHERE uuid = :uuid CASCADE"),
        {'uuid': malaren_uuid}
    )
