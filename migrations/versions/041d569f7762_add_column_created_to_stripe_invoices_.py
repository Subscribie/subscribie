"""add_column_created_to_stripe_invoices_table

Revision ID: 041d569f7762
Revises: c57ff5a7436a
Create Date: 2022-04-07 17:33:30.075127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "041d569f7762"
down_revision = "c57ff5a7436a"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("stripe_invoice") as batch_op:
        batch_op.add_column(sa.Column("created", sa.Integer(), nullable=True))


def downgrade():
    pass
