"""merge create module_seo_page_title table and add password_reset_string to users table

Revision ID: 31033c1cb05a
Revises: 0920b973dc64, b7a6209f6f9a
Create Date: 2020-08-02 17:13:41.825937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31033c1cb05a'
down_revision = ('0920b973dc64', 'b7a6209f6f9a')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
