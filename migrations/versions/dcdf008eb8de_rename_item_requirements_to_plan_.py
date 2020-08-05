"""rename item_requirements to plan_requirements

Revision ID: dcdf008eb8de
Revises: a24784861356
Create Date: 2020-08-03 15:46:03.290642

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcdf008eb8de'
down_revision = 'a24784861356'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('item_requirements', 'plan_requirements')


def downgrade():
    op.rename_table('plan_requirements', 'item_requirements')
