"""add stripe_webhook_endpoint_id to PaymentProvider

Revision ID: bca9e879f754
Revises: 5e536de32a31
Create Date: 2020-09-21 11:27:02.928338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bca9e879f754'
down_revision = '5e536de32a31'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.add_column(sa.Column('stripe_webhook_endpoint_id', sa.String(), nullable=True))


def downgrade():
    pass
