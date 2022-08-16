"""rename stripe webhook and account cols payment_provider

Revision ID: c5d444ee3ccd
Revises: 2c7e021d9a69
Create Date: 2020-11-02 11:31:22.184012

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c5d444ee3ccd"
down_revision = "2c7e021d9a69"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.alter_column(
            "stripe_webhook_endpoint_id",
            new_column_name="stripe_live_webhook_endpoint_id",
            existing_type=sa.String(255),
        )
        batch_op.alter_column(
            "stripe_webhook_endpoint_secret",
            new_column_name="stripe_live_webhook_endpoint_secret",
            existing_type=sa.String(255),
        )
        batch_op.alter_column(
            "stripe_connect_account_id",
            new_column_name="stripe_live_connect_account_id",
            existing_type=sa.String(255),
        )


def downgrade():
    pass
