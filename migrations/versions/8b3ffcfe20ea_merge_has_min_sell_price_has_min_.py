"""Merge has_min_sell_price has_min_interval_amount with is_donation

Revision ID: 8b3ffcfe20ea
Revises: 262c26af9630, 94790e701430
Create Date: 2023-05-15 13:31:13.027414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b3ffcfe20ea'
down_revision = ('262c26af9630', '94790e701430')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
