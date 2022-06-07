"""add PriceList model

Revision ID: 6ae2db9a982b
Revises: 54495b8316a1
Create Date: 2022-06-07 22:00:26.081464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6ae2db9a982b"
down_revision = "54495b8316a1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "price_list",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("expire_date", sa.DateTime(), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
