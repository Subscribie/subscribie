"""add module_style table

Revision ID: 38dad517daf6
Revises: 7da4a5f6cc70
Create Date: 2020-09-03 15:22:20.877099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '38dad517daf6'
down_revision = '7da4a5f6cc70'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('module_style',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('css', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
