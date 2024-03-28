"""add association_table_plan_to_users

Revision ID: d80effffd83d
Revises: 48074e6225c6
Create Date: 2024-02-12 12:24:44.482877

Why?

Some shop owners want/need to assign managers (users) to
plans. For example large clubs or membership organisations which
assign a 'manager' to one or more plans.

The plan_user_associations table begins to make possible the
assignment of Users to Plans. Recall that Users (see class User
in models.py) is a shop owner (admin) which may login to the
Subscribie application.

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d80effffd83d"
down_revision = "48074e6225c6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plan_user_associations",
        sa.Column("plan_uuid", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_uuid"],
            ["plan.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
    )


def downgrade():
    pass
