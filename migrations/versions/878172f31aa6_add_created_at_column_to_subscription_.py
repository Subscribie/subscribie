"""add created_at column to subscription table

Revision ID: 878172f31aa6
Revises: ab7bafa5e261
Create Date: 2020-04-24 22:49:28.571934

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '878172f31aa6'
down_revision = 'ab7bafa5e261'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.drop_column('created_at')
