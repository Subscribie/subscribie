"""correct store cancel_at at int

Revision ID: 2378e3286d5b
Revises: b3c13acc1013
Create Date: 2021-05-09 21:28:01.250318

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2378e3286d5b"
down_revision = "b3c13acc1013"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.alter_column(
            "cancel_at",
            type_=sa.Integer(),
            nullable=True,
            existing_type=sa.Boolean(),
            default=False,
        )

    with op.batch_alter_table("subscription") as batch_op:
        batch_op.alter_column(
            "stripe_cancel_at",
            type_=sa.Integer(),
            nullable=True,
            default=False,
            existing_type=sa.Boolean(),
        )


def downgrade():
    pass
