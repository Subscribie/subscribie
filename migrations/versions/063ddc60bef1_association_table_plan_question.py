"""association_table_plan_question

Revision ID: 063ddc60bef1
Revises: c5bec71f1499
Create Date: 2024-05-09 22:00:42.022150

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "063ddc60bef1"
down_revision = "c5bec71f1499"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plan_question_associations",
        sa.Column("question_id", sa.Integer(), nullable=True),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plan.id"],
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["question.id"],
        ),
    )


def downgrade():
    pass
