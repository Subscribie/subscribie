"""add interval_unit interval_amount to subscription

Revision ID: 5b308deca3d3
Revises: 6d9febd1346e
Create Date: 2022-07-25 22:27:45.930134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5b308deca3d3"
down_revision = "6d9febd1346e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column("interval_unit", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("interval_amount", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("sell_price", sa.Integer(), nullable=True))


def downgrade():
    pass
