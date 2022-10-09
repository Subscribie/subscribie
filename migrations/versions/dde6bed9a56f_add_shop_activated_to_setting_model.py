"""add shop_activated to setting model

Revision ID: dde6bed9a56f
Revises: 96430096c2c7
Create Date: 2022-01-25 10:04:41.225725

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dde6bed9a56f"
down_revision = "96430096c2c7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(sa.Column("shop_activated", sa.Boolean(), default=0))


def downgrade():
    pass
