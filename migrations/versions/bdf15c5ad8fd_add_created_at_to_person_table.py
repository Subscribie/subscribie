"""add created_at to Person table

Revision ID: bdf15c5ad8fd
Revises: 3c13f4c7200d
Create Date: 2020-04-25 15:37:14.775434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bdf15c5ad8fd'
down_revision = '3c13f4c7200d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("person") as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("person") as batch_op:
        batch_op.drop_column('created_at')
