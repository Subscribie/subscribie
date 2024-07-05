"""add stripe_user_attempted_checkout_flow to Subscription

Revision ID: 8c008c1333d5
Revises: 3447b58b5c69
Create Date: 2024-07-05 20:39:42.709426

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c008c1333d5"
down_revision = "3447b58b5c69"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "stripe_user_attempted_checkout_flow", sa.Boolean(), default=False
            )
        )


def downgrade():
    pass
