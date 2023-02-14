"""empty message

Revision ID: a233a79f7749
Revises: 7f3a2410fb7f
Create Date: 2023-02-13 22:47:36.155645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a233a79f7749"
down_revision = "7f3a2410fb7f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(sa.Column("donations", sa.String(), nullable=True))


def downgrade():
    pass
