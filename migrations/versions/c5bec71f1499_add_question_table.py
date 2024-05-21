"""add question table

Revision ID: c5bec71f1499
Revises: bb76d2149316
Create Date: 2024-05-08 21:30:41.805887

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c5bec71f1499"
down_revision = "bb76d2149316"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "question",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
