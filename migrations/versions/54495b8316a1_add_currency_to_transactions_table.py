"""add currency to Transactions table

Revision ID: 54495b8316a1
Revises: 98bd81ff72f9
Create Date: 2022-05-30 01:22:09.158426

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "54495b8316a1"
down_revision = "98bd81ff72f9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("transactions") as batch_op:
        batch_op.add_column(sa.Column("currency", sa.String(), nullable=True))


def downgrade():
    pass
