"""add order to association_table_plan_question

Revision ID: 3a54f4b1187d
Revises: 1d4b6d333c16
Create Date: 2024-05-19 18:13:11.397272

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3a54f4b1187d"
down_revision = "1d4b6d333c16"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan_question_associations", schema=None) as batch_op:
        batch_op.add_column(sa.Column("order", sa.Integer(), nullable=True))


def downgrade():
    pass
