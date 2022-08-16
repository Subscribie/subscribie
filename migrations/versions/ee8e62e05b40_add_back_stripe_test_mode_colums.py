"""add back stripe test mode colums

Revision ID: ee8e62e05b40
Revises: 686d588c3c29
Create Date: 2020-11-02 16:38:32.337427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ee8e62e05b40"
down_revision = "686d588c3c29"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.add_column(
            sa.Column("stripe_test_webhook_endpoint_id", sa.String(255), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "stripe_test_webhook_endpoint_secret", sa.String(255), nullable=True
            )
        )


def downgrade():
    pass
