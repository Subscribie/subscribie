"""empty message

Revision ID: 73b9ee072297
Revises: 00477315ded9
Create Date: 2022-06-01 14:05:53.103093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "73b9ee072297"
down_revision = "00477315ded9"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plan", sa.Column("currency", sa.String(), nullable=True))


def downgrade():
    pass
