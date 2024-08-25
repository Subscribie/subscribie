"""add mailchimp integration columns

Revision ID: abc1ff0c85e0
Revises: a4d35e9917f7
Create Date: 2024-08-25 13:14:48.912208

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "abc1ff0c85e0"
down_revision = "a4d35e9917f7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("integration", schema=None) as batch_op:
        batch_op.add_column(sa.Column("mailchimp_api_key", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("mailchimp_list_id", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("mailchimp_active", sa.Boolean(), nullable=True))


def downgrade():
    pass
