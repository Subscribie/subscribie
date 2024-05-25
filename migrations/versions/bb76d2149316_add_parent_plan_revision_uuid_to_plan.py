"""add parent_plan_revision_uuid to plan

Revision ID: bb76d2149316
Revises: 48074e6225c6
Create Date: 2024-02-16 23:22:02.230866

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bb76d2149316"
down_revision = "48074e6225c6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("parent_plan_revision_uuid", sa.String(), nullable=True)
        )


def downgrade():
    pass
