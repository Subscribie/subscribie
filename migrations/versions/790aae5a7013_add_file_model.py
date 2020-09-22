"""add File model

Revision ID: 790aae5a7013
Revises: 702d6ee9b14f
Create Date: 2020-09-22 14:45:14.686269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '790aae5a7013'
down_revision = '702d6ee9b14f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('file',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('uuid', sa.String(), nullable=True),
    sa.Column('file_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
