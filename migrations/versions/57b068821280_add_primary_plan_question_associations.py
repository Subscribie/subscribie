"""add primary plan_question_associations

Revision ID: 57b068821280
Revises: 3a54f4b1187d
Create Date: 2024-05-19 19:58:41.527688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "57b068821280"
down_revision = "3a54f4b1187d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan_question_associations", schema=None) as batch_op:
        batch_op.alter_column("question_id", existing_type=sa.INTEGER(), nullable=False)
        batch_op.alter_column("plan_id", existing_type=sa.INTEGER(), nullable=False)


def downgrade():
    pass
