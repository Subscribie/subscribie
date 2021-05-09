"""store cancel_at as int

Revision ID: b3c13acc1013
Revises: 084669093d74
Create Date: 2021-05-09 14:12:15.268759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b3c13acc1013"
down_revision = "084669093d74"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.alter_column(
            "cancel_at",
            type_=sa.Boolean(),
            nullable=True,
            existing_type=sa.String(),
            default=False,
        )

    with op.batch_alter_table("subscription") as batch_op:
        batch_op.alter_column(
            "stripe_cancel_at", type_=sa.Boolean(), nullable=True, default=False
        )


def downgrade():
    pass
