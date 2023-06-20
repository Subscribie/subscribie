"""add vat_percentage to settings model

Revision ID: 34ce0963d783
Revises: 7640c2a9be5b
Create Date: 2023-05-17 18:56:11.575557

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "34ce0963d783"
down_revision = "7640c2a9be5b"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "setting",
        sa.Column(
            "vat_percentage", sa.Float(), nullable=True, server_default=text("20.0")
        ),
    )


def downgrade():
    pass
