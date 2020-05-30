"""add page table migration

Revision ID: 356534365c6e
Revises: 252d0418696b
Create Date: 2020-05-30 14:38:04.560535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '356534365c6e'
down_revision = '252d0418696b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('page',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('page_name', sa.String(), nullable=True),
    sa.Column('path', sa.String(), nullable=True),
    sa.Column('template_file', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('page')
