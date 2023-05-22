"""add HasReadOnly read_only mixin to documents model

Revision ID: fbc611c57b7a
Revises: 94790e701430
Create Date: 2023-05-11 22:44:20.776241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fbc611c57b7a"
down_revision = "94790e701430"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("document", sa.Column("read_only", sa.Boolean(), nullable=True))


def downgrade():
    pass
