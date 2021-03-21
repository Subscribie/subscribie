"""so that categories may be ordered

Revision ID: 746b4765a957
Revises: b8e926d239f9
Create Date: 2021-03-21 15:21:16.472897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "746b4765a957"
down_revision = "b8e926d239f9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("category") as batch_op:
        batch_op.add_column(sa.Column("position", sa.Integer(), default=0))


def downgrade():
    pass
