"""add-donations-columns-in-settings

Revision ID: bd63fd27d653
Revises: 938b171f97ec
Create Date: 2023-02-15 13:54:54.675597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bd63fd27d653"
down_revision = "938b171f97ec"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting", schema=None) as batch_op:
        batch_op.add_column(sa.Column("donations_enabled", sa.Boolean(), nullable=True))


def downgrade():
    pass
