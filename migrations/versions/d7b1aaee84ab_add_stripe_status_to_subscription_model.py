"""add stripe_status to subscription model

Revision ID: d7b1aaee84ab
Revises: c751fe53a042
Create Date: 2021-05-01 23:05:25.344813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d7b1aaee84ab"
down_revision = "c751fe53a042"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column("stripe_status", sa.String(255), nullable=True))


def downgrade():
    pass
