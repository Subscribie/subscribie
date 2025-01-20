"""Merge abfb5c2f77e6 SpamEmailDomain and d8c120e8212e add proration_behavior stripe_proration_behavior

Revision ID: 08dcbc5f9c6d
Revises: abfb5c2f77e6, d8c120e8212e
Create Date: 2025-01-20 21:23:49.963312

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08dcbc5f9c6d'
down_revision = ('abfb5c2f77e6', 'd8c120e8212e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
