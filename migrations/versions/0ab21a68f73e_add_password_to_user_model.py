"""add password to user model

Revision ID: 0ab21a68f73e
Revises: e8f1a3d0001f
Create Date: 2020-06-21 13:46:26.001236

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ab21a68f73e'
down_revision = 'e8f1a3d0001f'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(), nullable=True))

def downgrade():
    pass
