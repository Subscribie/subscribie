"""added stripe pause collection to Transaction table

Revision ID: 96430096c2c7
Revises: b3f47a3f53e2
Create Date: 2021-07-12 20:12:29.813558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "96430096c2c7"
down_revision = "b3f47a3f53e2"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "subscription", sa.Column("stripe_pause_collection", sa.String(255), nullable=True)
    )


def downgrade():
    pass
