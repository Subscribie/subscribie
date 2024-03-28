"""add catagory_user_associations

Revision ID: 9083452d3a80
Revises: 48074e6225c6
Create Date: 2024-02-16 21:38:11.302398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9083452d3a80"
down_revision = "48074e6225c6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "catagory_user_associations",
        sa.Column("category_uuid", sa.String(), nullable=True),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_uuid"],
            ["category.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
    )


def downgrade():
    pass
