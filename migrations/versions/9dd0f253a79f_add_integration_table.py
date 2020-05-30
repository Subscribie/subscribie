"""add integration table

Revision ID: 9dd0f253a79f
Revises: 87387dc56edd
Create Date: 2020-05-30 14:24:53.402496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dd0f253a79f'
down_revision = '87387dc56edd'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('integration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('google_tag_manager_active', sa.Boolean(), nullable=True),
    sa.Column('google_tag_manager_container_id', sa.String(), nullable=True),
    sa.Column('tawk_active', sa.Boolean(), nullable=True),
    sa.Column('tawk_property_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('integration')
