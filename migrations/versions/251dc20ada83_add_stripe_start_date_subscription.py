"""add stripe_start_date subscription

Revision ID: 251dc20ada83
Revises: a4d35e9917f7
Create Date: 2024-08-08 21:13:14.731101

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "251dc20ada83"
down_revision = "a4d35e9917f7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.add_column(sa.Column("stripe_start_date", sa.Integer(), nullable=True))


def downgrade():
    pass
