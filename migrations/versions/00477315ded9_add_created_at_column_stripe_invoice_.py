"""add_created_at_column_stripe_invoice_table

Revision ID: 00477315ded9
Revises: 041d569f7762
Create Date: 2022-04-07 17:49:50.146114

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "00477315ded9"
down_revision = "041d569f7762"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("stripe_invoice") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade():
    pass
