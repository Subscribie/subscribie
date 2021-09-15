"""add stripe_payment_intent_id Transaction table

Revision ID: 6d25fcf6fbc8
Revises: 96430096c2c7
Create Date: 2021-09-10 21:52:53.363829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6d25fcf6fbc8"
down_revision = "96430096c2c7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(
            sa.Column("stripe_payment_intent_id", sa.String(), nullable=True),
        )


def downgrade():
    pass
