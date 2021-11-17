"""add css_properties_json remove bg_primary column

Revision ID: fd28aefcdb76
Revises: 6cc0e87e8836
Create Date: 2021-01-16 13:12:55.795750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fd28aefcdb76"
down_revision = "6cc0e87e8836"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("module_style") as batch_op:
        batch_op.add_column(
            sa.Column("css_properties_json", sa.String(255), nullable=True)
        )
        batch_op.drop_column("bg_primary")


def downgrade():
    pass
