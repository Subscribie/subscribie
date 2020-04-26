"""add gocardless subscription id to subscriptions table

Revision ID: 3c13f4c7200d
Revises: 878172f31aa6
Create Date: 2020-04-24 23:57:09.740413

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c13f4c7200d'
down_revision = '878172f31aa6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column('gocardless_subscription_id', sa.String(), nullable=True))


def downgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.drop_column('gocardless_subscription_id')
