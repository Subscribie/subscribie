"""add bg-primary to ModuleStyle model

Revision ID: 6cc0e87e8836
Revises: 8d9ada7a21cd
Create Date: 2021-01-10 16:53:43.057712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6cc0e87e8836"
down_revision = "8d9ada7a21cd"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("module_style") as batch_op:
        batch_op.add_column(sa.Column("bg_primary", sa.String(), nullable=True))


def downgrade():
    pass
