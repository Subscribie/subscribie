"""add api_key_secret_live api_key_secret_test to secret model

Revision ID: 7fba2877d034
Revises: dde6bed9a56f
Create Date: 2022-03-08 01:43:18.744690

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7fba2877d034"
down_revision = "dde6bed9a56f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(
            sa.Column("api_key_secret_live", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("api_key_secret_test", sa.String(), nullable=True)
        )


def downgrade():
    pass
