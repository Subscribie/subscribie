"""add has_min_sell_price has_min_interval_amount

Revision ID: 262c26af9630
Revises: 938b171f97ec
Create Date: 2022-12-23 14:50:18.143177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "262c26af9630"
down_revision = "938b171f97ec"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("price_list_rule") as batch_op:
        batch_op.add_column(
            sa.Column("has_min_sell_price", sa.Boolean(), nullable=True)
        )

    with op.batch_alter_table("price_list_rule") as batch_op:
        batch_op.add_column(
            sa.Column("has_min_interval_amount", sa.Boolean(), nullable=True)
        )


def downgrade():
    pass
