"""remove-dingdb

Revision ID: 1928f415df34
Revises: 5be4d91c4db1
Create Date: 2020-05-20 21:20:55.473878

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1928f415df34'
down_revision = '5be4d91c4db1'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table('data')
    op.drop_table('ding')
    op.drop_table('version')


def downgrade():
    op.create_table('version',
    sa.Column('pk', sa.INTEGER(), nullable=False),
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('ding_id', sa.VARCHAR(), nullable=True),
    sa.Column('creator', sa.VARCHAR(), nullable=True),
    sa.Column('creation_date', sa.VARCHAR(), nullable=True),
    sa.Column('comment', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('pk')
    )
    op.create_table('ding',
    sa.Column('pk', sa.INTEGER(), nullable=False),
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=True),
    sa.Column('kind_id', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('pk')
    )
    op.create_table('data',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('ding_id', sa.VARCHAR(), nullable=True),
    sa.Column('version_id', sa.VARCHAR(), nullable=True),
    sa.Column('key', sa.VARCHAR(), nullable=True),
    sa.Column('value', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
