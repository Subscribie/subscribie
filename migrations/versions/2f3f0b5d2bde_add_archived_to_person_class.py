"""add archived to Person class

Revision ID: 2f3f0b5d2bde
Revises: 500f2d55c5d3
Create Date: 2021-02-28 23:13:51.486171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2f3f0b5d2bde"
down_revision = "500f2d55c5d3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("person") as batch_op:
        batch_op.add_column(
            sa.Column("archived", sa.Boolean(), nullable=False, default=False)
        )


def downgrade():
    pass
