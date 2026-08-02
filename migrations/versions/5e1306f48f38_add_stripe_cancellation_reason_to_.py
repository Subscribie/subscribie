"""add stripe_cancellation_reason to subscription model

Revision ID: 5e1306f48f38
Revises: 08dcbc5f9c6d
Create Date: 2026-04-21 21:10:30.829860

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5e1306f48f38"
down_revision = "08dcbc5f9c6d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("stripe_cancellation_reason", sa.String(), nullable=True)
        )


def downgrade():
    pass
