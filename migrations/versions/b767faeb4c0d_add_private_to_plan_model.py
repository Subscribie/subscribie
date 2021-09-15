"""add private to plan model

Revision ID: b767faeb4c0d
Revises: 21b64f9d73dd
Create Date: 2021-03-27 00:26:17.579713

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b767faeb4c0d"
down_revision = "21b64f9d73dd"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column("private", sa.Boolean(), default=False))


def downgrade():
    pass
