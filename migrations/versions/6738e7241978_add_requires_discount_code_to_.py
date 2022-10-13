"""add requires_discount_code to PriceListRule

Revision ID: 6738e7241978
Revises: e9e1f148655e
Create Date: 2022-06-29 19:23:53.498096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6738e7241978"
down_revision = "e9e1f148655e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("price_list_rule") as batch_op:
        batch_op.add_column(
            sa.Column("requires_discount_code", sa.Boolean(), default=False),
        )


def downgrade():
    pass
