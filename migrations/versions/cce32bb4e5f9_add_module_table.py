"""add module table

Revision ID: cce32bb4e5f9
Revises: 356534365c6e
Create Date: 2020-05-30 14:44:46.372032

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cce32bb4e5f9'
down_revision = '356534365c6e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('module',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('src', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('module')
