"""add default_country_code to settings table

Revision ID: e0a8901cde76
Revises: f064a641532c
Create Date: 2022-10-06 00:04:42.866952

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e0a8901cde76"
down_revision = "f064a641532c"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(
            sa.Column("default_country_code", sa.String(), nullable=True)
        )


def downgrade():
    pass
