"""add description to plan model

Revision ID: 8d9ada7a21cd
Revises: 98099ff3eb9c
Create Date: 2021-01-02 21:00:51.067229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8d9ada7a21cd"
down_revision = "98099ff3eb9c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column("description", sa.String(255), nullable=True))


def downgrade():
    pass
