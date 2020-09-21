"""add stripe_webhook_endpoint_secret to PaymentProvider

Revision ID: 5e536de32a31
Revises: db265b2a50e1
Create Date: 2020-09-21 11:16:08.945258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e536de32a31'
down_revision = 'db265b2a50e1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.add_column(sa.Column('stripe_webhook_endpoint_secret', sa.String(), nullable=True))


def downgrade():
    pass
