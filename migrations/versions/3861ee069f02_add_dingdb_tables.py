"""add dingdb tables

Revision ID: 3861ee069f02
Revises: bdf15c5ad8fd
Create Date: 2020-04-25 18:07:01.477520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3861ee069f02'
down_revision = 'bdf15c5ad8fd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ding_id', sa.String(), nullable=True),
    sa.Column('version_id', sa.String(), nullable=True),
    sa.Column('key', sa.String(), nullable=True),
    sa.Column('value', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ding',
    sa.Column('pk', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('kind_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('pk')
    )
    op.create_table('version',
    sa.Column('pk', sa.Integer(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('ding_id', sa.String(), nullable=True),
    sa.Column('creator', sa.String(), nullable=True),
    sa.Column('creation_date', sa.String(), nullable=True),
    sa.Column('comment', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('pk')
    )

def downgrade():
    op.drop_table('version')
    op.drop_table('ding')
    op.drop_table('data')
