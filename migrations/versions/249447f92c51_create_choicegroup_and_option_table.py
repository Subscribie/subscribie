"""create ChoiceGroup and Option table

Revision ID: 249447f92c51
Revises: 6897fb668ec5
Create Date: 2020-08-05 16:02:34.797265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '249447f92c51'
down_revision = '6897fb668ec5'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('choice_group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('option',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('choice_group_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('primary_icon', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['choice_group_id'], ['choice_group.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    pass
