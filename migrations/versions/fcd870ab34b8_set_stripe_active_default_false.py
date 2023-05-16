"""Set stripe_active default false

Revision ID: fcd870ab34b8
Revises: 00477315ded9
Create Date: 2022-09-12 14:37:30.182327

"""
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = "fcd870ab34b8"
down_revision = "00477315ded9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.alter_column(
            "stripe_active",
            server_default=text("0"),
        )


def downgrade():
    pass
