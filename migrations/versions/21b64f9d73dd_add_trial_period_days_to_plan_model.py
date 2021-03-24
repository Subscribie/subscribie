"""add trial_period_days to Plan model

Revision ID: 21b64f9d73dd
Revises: d04243b7bd47
Create Date: 2021-03-24 22:54:05.568960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "21b64f9d73dd"
down_revision = "d04243b7bd47"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column("trial_period_days", sa.Integer(), default=0))


def downgrade():
    pass
