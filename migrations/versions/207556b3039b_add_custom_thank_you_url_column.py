"""add custom thank you url column

Revision ID: 207556b3039b
Revises: 7640c2a9be5b
Create Date: 2023-09-01 19:35:12.241628

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "207556b3039b"
down_revision = "7640c2a9be5b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "setting", sa.Column("custom_thank_you_url", sa.String(), nullable=True)
    )


def downgrade():
    pass
