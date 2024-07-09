"""add geo_currency_enabled to settings

Revision ID: a4d35e9917f7
Revises: 8c008c1333d5
Create Date: 2024-07-09 04:21:25.517787

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a4d35e9917f7"
down_revision = "8c008c1333d5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "geo_currency_enabled", sa.Boolean(), nullable=True, default=False
            )
        )


def downgrade():
    pass
