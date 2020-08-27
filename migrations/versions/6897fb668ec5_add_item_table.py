"""add item table

Revision ID: 6897fb668ec5
Revises: b6d224b6e151
Create Date: 2020-08-04 20:39:31.187548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6897fb668ec5'
down_revision = 'b6d224b6e151'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('item',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    pass
