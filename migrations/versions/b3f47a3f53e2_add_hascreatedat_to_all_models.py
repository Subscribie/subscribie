"""add HasCreatedAt to all models

Revision ID: b3f47a3f53e2
Revises: 3a8f3089d09d
Create Date: 2021-06-05 14:52:15.700299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b3f47a3f53e2"
down_revision = "3a8f3089d09d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("email_template") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("login_token") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("module_seo_page_title") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade():
    pass
