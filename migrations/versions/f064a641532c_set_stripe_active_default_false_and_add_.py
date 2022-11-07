"""Set stripe_active default false and add interval_unit interval_amount to subscription

Revision ID: f064a641532c
Revises: fcd870ab34b8, 5b308deca3d3
Create Date: 2022-09-13 12:18:31.520291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f064a641532c"
down_revision = ("fcd870ab34b8", "5b308deca3d3")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
