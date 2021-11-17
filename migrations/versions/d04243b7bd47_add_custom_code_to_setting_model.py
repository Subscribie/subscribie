"""add custom_code to Setting model

Revision ID: d04243b7bd47
Revises: 746b4765a957
Create Date: 2021-03-24 18:16:54.944191

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d04243b7bd47"
down_revision = "746b4765a957"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("setting") as batch_op:
        batch_op.add_column(sa.Column("custom_code", sa.String(255), nullable=True))


def downgrade():
    pass
