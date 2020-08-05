"""default interval_unit to monthly on items table where null

Revision ID: 61dc9ffd0ef0
Revises: 1e10cc023d31
Create Date: 2020-07-30 20:37:55.342225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61dc9ffd0ef0'
down_revision = '1e10cc023d31'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE item SET interval_unit='monthly' WHERE interval_unit IS NULL;")

def downgrade():
    pass
