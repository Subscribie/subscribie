"""add interval_unit to item table

Revision ID: 3d52613014d5
Revises: 52be33302614
Create Date: 2020-07-25 16:12:53.427725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d52613014d5'
down_revision = '52be33302614'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('item') as batch_op:
        batch_op.add_column(sa.Column('interval_unit', sa.String(), nullable=True))

def downgrade():
    pass
