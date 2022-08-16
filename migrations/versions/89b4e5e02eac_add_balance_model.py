"""add balance model

Revision ID: 89b4e5e02eac
Revises: dde6bed9a56f
Create Date: 2022-02-22 22:14:55.030280

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "89b4e5e02eac"
down_revision = "dde6bed9a56f"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "balance",
        sa.Column("uuid", sa.String(255), nullable=False),
        sa.Column("available_amount", sa.Integer(), nullable=True),
        sa.Column("available_currency", sa.String(255), nullable=True),
        sa.Column("stripe_livemode", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("uuid"),
    )


def downgrade():
    pass
