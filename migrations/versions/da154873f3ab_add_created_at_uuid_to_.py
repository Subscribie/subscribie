"""add created_at uuid to PlanQuestionAssociation

Revision ID: da154873f3ab
Revises: 57b068821280
Create Date: 2024-05-19 21:59:10.555714

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "da154873f3ab"
down_revision = "57b068821280"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan_question_associations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("uuid", sa.String(), nullable=True))


def downgrade():
    pass
