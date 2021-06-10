"""add stripe_cancel_at to Subscription model

Revision ID: 084669093d74
Revises: b28487bfca0f
Create Date: 2021-05-04 22:55:42.753614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "084669093d74"
down_revision = "b28487bfca0f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column("stripe_cancel_at", sa.String(), nullable=True))


def downgrade():
    pass
