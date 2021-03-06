"""add stripe_livemode column to TaxRate model

Revision ID: e0919a39645f
Revises: 796ff2e47e13
Create Date: 2021-03-06 18:23:31.252540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e0919a39645f"
down_revision = "796ff2e47e13"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tax_rate") as batch_op:
        batch_op.add_column(sa.Column("stripe_livemode", sa.Boolean()))


def downgrade():
    pass
