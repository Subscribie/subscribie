"""add is_longform_question to question

Revision ID: 3447b58b5c69
Revises: da154873f3ab
Create Date: 2024-06-17 21:31:27.252460

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3447b58b5c69"
down_revision = "da154873f3ab"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("question", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_longform_question", sa.Boolean(), nullable=True, default=False
            )
        )


def downgrade():
    pass
