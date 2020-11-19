"""add private boolean to pages model

Revision ID: 9189f7033477
Revises: 1653ed33cbd4
Create Date: 2020-11-19 11:40:21.304451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9189f7033477"
down_revision = "1653ed33cbd4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("page") as batch_op:
        batch_op.add_column(sa.Column("private", sa.Boolean, default=False))


def downgrade():
    pass
