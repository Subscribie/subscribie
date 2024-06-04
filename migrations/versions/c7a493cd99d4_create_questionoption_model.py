"""create QuestionOption model

Revision ID: c7a493cd99d4
Revises: c70cd4900c96
Create Date: 2024-05-18 20:02:36.104426

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7a493cd99d4"
down_revision = "c70cd4900c96"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "question_option",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("primary_icon", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["question.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("question", schema=None) as batch_op:
        batch_op.alter_column("uuid", existing_type=sa.VARCHAR(), nullable=True)
        batch_op.alter_column("created_at", existing_type=sa.DATETIME(), nullable=True)
        batch_op.alter_column("title", existing_type=sa.VARCHAR(), nullable=True)


def downgrade():
    pass
