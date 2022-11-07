"""addassociation_table_price_list_to_rule

Revision ID: 75dffc3851d8
Revises: 4e7e3ee8972d
Create Date: 2022-06-19 17:47:37.281829

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "75dffc3851d8"
down_revision = "4e7e3ee8972d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "price_list_rules_associations",
        sa.Column("price_list_uuid", sa.Integer(), nullable=False),
        sa.Column("price_list_rule_uuid", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["price_list_rule_uuid"],
            ["price_list_rule.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["price_list_uuid"],
            ["price_list.uuid"],
        ),
    )


def downgrade():
    pass
