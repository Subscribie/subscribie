"""add fulfillment_state to transactions table

Revision ID: b847ac773b5f
Revises: 0ab21a68f73e
Create Date: 2020-06-22 19:25:56.603046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b847ac773b5f'
down_revision = '0ab21a68f73e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(sa.Column('fulfillment_state', sa.String(), nullable=True))


def downgrade():
    pass
