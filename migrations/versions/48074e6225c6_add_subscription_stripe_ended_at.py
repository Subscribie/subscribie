"""add subscription stripe_ended_at

Revision ID: 48074e6225c6
Revises: 207556b3039b
Create Date: 2024-02-11 17:21:19.287478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "48074e6225c6"
down_revision = "207556b3039b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.add_column(sa.Column("stripe_ended_at", sa.Integer(), nullable=True))


def downgrade():
    pass
