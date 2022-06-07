"""add PriceListRule model

Revision ID: 4e7e3ee8972d
Revises: 6ae2db9a982b
Create Date: 2022-06-07 22:47:55.495926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4e7e3ee8972d"
down_revision = "6ae2db9a982b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "price_list_rule",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("expire_date", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("affects_sell_price", sa.Boolean(), nullable=True),
        sa.Column("affects_interval_amount", sa.Boolean(), nullable=True),
        sa.Column("percent_discount", sa.Integer(), nullable=True),
        sa.Column("percent_increase", sa.Integer(), nullable=True),
        sa.Column("amount_discount", sa.Integer(), nullable=True),
        sa.Column("amount_increase", sa.Integer(), nullable=True),
        sa.Column("min_sell_price", sa.Integer(), nullable=True),
        sa.Column("min_interval_amount", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
