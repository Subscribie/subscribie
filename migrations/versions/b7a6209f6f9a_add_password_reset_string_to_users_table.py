"""add password_reset_string to users table

Revision ID: b7a6209f6f9a
Revises: 61dc9ffd0ef0
Create Date: 2020-08-01 15:56:16.071171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7a6209f6f9a'
down_revision = '61dc9ffd0ef0'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('password_reset_string', sa.String(), nullable=True))


def downgrade():
    pass
