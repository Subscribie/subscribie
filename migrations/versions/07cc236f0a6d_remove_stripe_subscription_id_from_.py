"""remove stripe_subscription_id from Subscription model

Revision ID: 07cc236f0a6d
Revises: f3579efd3331
Create Date: 2020-12-04 14:59:11.346386

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "07cc236f0a6d"
down_revision = "f3579efd3331"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.drop_column("stripe_subscription_id")


def downgrade():
    pass
