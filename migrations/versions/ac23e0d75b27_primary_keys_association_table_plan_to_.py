"""primary keys association_table_plan_to_users

Revision ID: ac23e0d75b27
Revises: ba57f5aeba5f
Create Date: 2024-02-24 16:15:56.898449

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData, Table, Column, Integer, String


# revision identifiers, used by Alembic.
revision = "ac23e0d75b27"
down_revision = "ba57f5aeba5f"
branch_labels = None
depends_on = None


def upgrade():
    meta = MetaData()
    some_table = Table(
        "plan_user_associations",
        meta,
        Column("plan_uuid", String, nullable=False),
        Column("user_id", Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ["plan_uuid"],
            ["plan.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("plan_uuid", "user_id"),
    )

    with op.batch_alter_table(
        "plan_user_associations", copy_from=some_table
    ) as batch_op:
        batch_op.create_primary_key(
            "pk_plan_user_association", ["plan_uuid", "user_id"]
        )


def downgrade():
    pass
