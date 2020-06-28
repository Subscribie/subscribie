"""add payment_status to transactions table

Revision ID: 52be33302614
Revises: b847ac773b5f
Create Date: 2020-06-22 20:20:49.880890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '52be33302614'
down_revision = 'b847ac773b5f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('transactions') as batch_op:
        batch_op.add_column(sa.Column('payment_status', sa.String(), nullable=True))


def downgrade():
    pass
