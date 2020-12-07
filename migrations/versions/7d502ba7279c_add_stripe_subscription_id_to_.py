"""add stripe_subscription_id to Subscription model

Revision ID: 7d502ba7279c
Revises: 1653ed33cbd4
Create Date: 2020-11-13 12:02:40.496271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d502ba7279c"
down_revision = "1653ed33cbd4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(
            sa.Column("stripe_subscription_id", sa.String(), nullable=True)
        )


def downgrade():
    pass
