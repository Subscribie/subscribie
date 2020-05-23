"""add company table

Revision ID: 36b57075d761
Revises: fa3e8029d9cb
Create Date: 2020-05-23 13:58:34.367085

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36b57075d761'
down_revision = 'fa3e8029d9cb'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('company',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('slogan', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('company')
