"""add interval_amount to item table

Revision ID: 9624c9410a7a
Revises: 3d52613014d5
Create Date: 2020-07-25 16:32:07.775424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9624c9410a7a'
down_revision = '3d52613014d5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('item') as batch_op:
        batch_op.add_column(sa.Column('interval_amount', sa.Integer(), nullable=True))


def downgrade():
    pass
