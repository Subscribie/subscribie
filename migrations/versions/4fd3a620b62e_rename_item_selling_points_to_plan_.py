"""rename item_selling_points to plan_selling_points

Revision ID: 4fd3a620b62e
Revises: dcdf008eb8de
Create Date: 2020-08-03 15:51:14.885900

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fd3a620b62e'
down_revision = 'dcdf008eb8de'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('item_selling_points', 'plan_selling_points')

def downgrade():
    op.rename_table('plan_selling_points', 'item_selling_points')
