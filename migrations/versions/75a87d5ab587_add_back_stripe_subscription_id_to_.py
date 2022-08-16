"""add back stripe_subscription_id to Subscription model

Revision ID: 75a87d5ab587
Revises: 07cc236f0a6d
Create Date: 2020-12-04 18:07:10.195939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "75a87d5ab587"
down_revision = "07cc236f0a6d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(
            sa.Column("stripe_subscription_id", sa.String(255), nullable=True)
        )


def downgrade():
    pass
