"""create module_seo_page_title table

Revision ID: 0920b973dc64
Revises: 61dc9ffd0ef0
Create Date: 2020-08-02 16:03:29.682881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0920b973dc64'
down_revision = '61dc9ffd0ef0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('module_seo_page_title',
    sa.Column('path', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('path')
    )


def downgrade():
    pass
