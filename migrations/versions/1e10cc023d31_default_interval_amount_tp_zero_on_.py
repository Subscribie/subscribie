"""default interval_amount tp zero on items table

Revision ID: 1e10cc023d31
Revises: 8755cd559d65
Create Date: 2020-07-30 20:36:06.366763

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e10cc023d31'
down_revision = '8755cd559d65'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE item SET interval_amount=0 WHERE interval_amount IS NULL")

def downgrade():
    pass
