"""feature_can_assign_users_to_plans settings

Revision ID: c4c7bbe1acdc
Revises: ac23e0d75b27
Create Date: 2024-02-26 09:06:42.508631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4c7bbe1acdc"
down_revision = "ac23e0d75b27"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "feature_can_assign_users_to_plans",
                sa.Boolean(),
                nullable=True,
                default=False,
            )
        )


def downgrade():
    pass
