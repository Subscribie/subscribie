"""add stripe_external_id to Subscription model

Revision ID: f3579efd3331
Revises: 7d502ba7279c
Create Date: 2020-12-04 14:51:09.699273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f3579efd3331"
down_revision = "7d502ba7279c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column("stripe_external_id", sa.String(), nullable=True))


def downgrade():
    pass
