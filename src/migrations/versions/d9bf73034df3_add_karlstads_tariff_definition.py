"""Add Karlstads tariff definition

Revision ID: d9bf73034df3
Revises: ca73d0a577a9
Create Date: 2025-05-22 11:48:23.954934+00:00

"""
from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ARRAY, UUID
from sqlalchemy.dialects.postgresql import JSONB

from engrate_sdk.utils.uuid import uuid7

# revision identifiers, used by Alembic.
revision: str = 'd9bf73034df3'
down_revision: Union[str, None] = '7c2a48fa940a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

karlstad_uuid = uuid7()
tariff_uid = uuid7()
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
            schema = 'power_tariffs'
        ),
        [
            {'uid':karlstad_uuid,'name': u'Karlstads Elnät AB', 'org_number': '556071-6085', 'ediel': 24300, 'active': True}
        ],
    )

    valid_from = datetime.strptime('01-01-2025', '%d-%m-%Y')
    valid_to = datetime.strptime('31-12-2025', '%d-%m-%Y')
    last_updated = datetime.now()


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
                'provider_uid': karlstad_uuid,
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
                'building_types': ['detached_house', 'terraced_house', 'summer_house']
            }
        ]
    )

    intervals = [
        {
            "from": "00:00",
            "to": "23:59",
            "multiplier": 1
        }
    ]

    # Create hints with region information
    hints = [
        {
            "type": "geolocation",
            "value": "Karlstad"
        },
        {
            "type": "model",
            "value": "single_peak"
        }
    ]

    # Insert tariff_compositions data
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
                'days': ['M', 'T', 'W', 'T', 'F', 'S', 'S'],
                'fuse_from': '16A',
                'fuse_to': '63A',
                'hints': hints,
                'unit': 'kr/kw',
                'price_exc_vat': 32.58,
                'price_inc_vat': 43.55,
                'intervals': intervals
            }
        ]
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM power_tariffs.providers WHERE uuid = :uuid CASCADE"),
        {'uuid': karlstad_uuid}
    )

