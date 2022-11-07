"""add stripe_livemode to payment_provider

Revision ID: f0e91df9fbf1
Revises: 3abcbb0428ef
Create Date: 2020-10-01 16:30:38.155152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0e91df9fbf1"
down_revision = "3abcbb0428ef"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.add_column(sa.Column("stripe_livemode", sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.drop_column("stripe_livemode")
