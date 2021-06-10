"""add cancel_at to plan model

Revision ID: c39dd6d1961f
Revises: c751fe53a042
Create Date: 2021-04-25 15:29:11.034541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c39dd6d1961f"
down_revision = "c751fe53a042"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column("cancel_at", sa.String(), nullable=True))


def downgrade():
    pass
