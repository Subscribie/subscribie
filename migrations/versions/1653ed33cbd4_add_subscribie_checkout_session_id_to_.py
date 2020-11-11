"""add subscribie_checkout_session_id to Subscription

Revision ID: 1653ed33cbd4
Revises: ee8e62e05b40
Create Date: 2020-11-11 12:08:45.878277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1653ed33cbd4"
down_revision = "ee8e62e05b40"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(
            sa.Column("subscribie_checkout_session_id", sa.String(), nullable=True)
        )


def downgrade():
    pass
