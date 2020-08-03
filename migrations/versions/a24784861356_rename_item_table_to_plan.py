"""rename item table to plan

Revision ID: a24784861356
Revises: 31033c1cb05a
Create Date: 2020-08-03 14:54:27.354165

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a24784861356'
down_revision = '31033c1cb05a'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('item', 'plan')

def downgrade():
    op.rename_table('plan', 'item')
