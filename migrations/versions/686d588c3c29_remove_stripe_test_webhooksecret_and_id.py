"""remove stripe test webhooksecret and id

Revision ID: 686d588c3c29
Revises: 56e852d799d1
Create Date: 2020-11-02 15:22:00.449292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "686d588c3c29"
down_revision = "56e852d799d1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.drop_column("stripe_test_webhook_endpoint_id")
        batch_op.drop_column("stripe_test_webhook_endpoint_secret")


def downgrade():
    pass
