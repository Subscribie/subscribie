"""add association_table_plan_to_price_lists

Revision ID: e9e1f148655e
Revises: 75dffc3851d8
Create Date: 2022-06-19 22:31:08.394131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e9e1f148655e"
down_revision = "75dffc3851d8"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "plan_price_list_associations",
        sa.Column("plan_uuid", sa.String(), nullable=False),
        sa.Column("price_list_uuid", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plan_uuid"],
            ["plan.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["price_list_uuid"],
            ["price_list.uuid"],
        ),
    )


def downgrade():
    pass
