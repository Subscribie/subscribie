"""remove unused item table

Revision ID: 7da4a5f6cc70
Revises: 4a72413f3d7a
Create Date: 2020-08-20 16:16:59.324850

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7da4a5f6cc70'
down_revision = '4a72413f3d7a'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('item')

def downgrade():
    op.create_table('item',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
