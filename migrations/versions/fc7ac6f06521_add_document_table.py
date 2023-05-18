"""add Document table

Revision ID: fc7ac6f06521
Revises: e0a8901cde76
Create Date: 2022-11-16 22:56:12.898374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fc7ac6f06521"
down_revision = "e0a8901cde76"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "document",
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column("body", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
