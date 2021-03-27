"""add hidden to plan model

Revision ID: e12b4fc15fe2
Revises: 21b64f9d73dd
Create Date: 2021-03-27 00:15:11.090276

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e12b4fc15fe2"
down_revision = "21b64f9d73dd"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(
            sa.Column("hidden", sa.Boolean(), nullable=True, default=False)
        )


def downgrade():
    pass
