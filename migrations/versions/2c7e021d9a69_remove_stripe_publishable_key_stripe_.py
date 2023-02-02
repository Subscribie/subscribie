"""remove stripe_publishable_key & stripe_secret_key from model

Revision ID: 2c7e021d9a69
Revises: f0e91df9fbf1
Create Date: 2020-11-02 11:21:21.027943

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "2c7e021d9a69"
down_revision = "f0e91df9fbf1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.drop_column("stripe_publishable_key")
        batch_op.drop_column("stripe_secret_key")


def downgrade():
    pass
