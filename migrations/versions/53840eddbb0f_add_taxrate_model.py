"""add TaxRate model

Revision ID: 53840eddbb0f
Revises: 2f3f0b5d2bde
Create Date: 2021-03-06 17:26:15.092902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "53840eddbb0f"
down_revision = "2f3f0b5d2bde"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tax_rate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stripe_tax_rate_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
