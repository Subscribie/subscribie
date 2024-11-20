"""add proration_behavior stripe_proration_behavior plan subscription

Revision ID: d8c120e8212e
Revises: a4d35e9917f7
Create Date: 2024-07-27 22:21:26.823294

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d8c120e8212e"
down_revision = "a4d35e9917f7"
branch_labels = None
depends_on = None


def upgrade():
    # "none" not to be confused with "None"
    # See
    # https://docs.stripe.com/api/subscriptions/create#create_subscription-proration_behavior
    with op.batch_alter_table("plan", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("proration_behavior", sa.String(), nullable=True, default="none")
        )

    # "none" not to be confused with "None"
    # See
    # https://docs.stripe.com/api/subscriptions/create#create_subscription-proration_behavior
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "stripe_proration_behavior", sa.String(), nullable=True, default="none"
            )
        )


def downgrade():
    pass
