"""add charge_vat to Setting model

Revision ID: 796ff2e47e13
Revises: 53840eddbb0f
Create Date: 2021-03-06 17:54:23.800916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "796ff2e47e13"
down_revision = "53840eddbb0f"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(sa.Column("charge_vat", sa.Boolean(), default=False))


def downgrade():
    pass
