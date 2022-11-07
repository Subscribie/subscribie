"""add default_currency to setting

Revision ID: 5d8da4e0a709
Revises: 96430096c2c7
Create Date: 2022-01-09 23:51:16.207317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d8da4e0a709"
down_revision = "96430096c2c7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(sa.Column("default_currency", sa.String(), nullable=True))


def downgrade():
    pass
