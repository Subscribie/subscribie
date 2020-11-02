"""add stripe webhook test columns

Revision ID: 56e852d799d1
Revises: c5d444ee3ccd
Create Date: 2020-11-02 11:54:29.263880

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "56e852d799d1"
down_revision = "c5d444ee3ccd"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.add_column(
            sa.Column("stripe_test_connect_account_id", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("stripe_test_webhook_endpoint_id", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("stripe_test_webhook_endpoint_secret", sa.String(), nullable=True)
        )


def downgrade():
    pass
