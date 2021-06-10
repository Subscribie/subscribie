"""add password_expired to user and subscriber models

Revision ID: c48dccfb0df5
Revises: 2378e3286d5b
Create Date: 2021-05-22 14:07:47.465185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c48dccfb0df5"
down_revision = "2378e3286d5b"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("person") as batch_op:
        batch_op.add_column(sa.Column("password_expired", sa.Boolean(), nullable=True))

    with op.batch_alter_table("user") as batch_op:
        batch_op.add_column(sa.Column("password_expired", sa.Boolean(), nullable=True))


def downgrade():
    pass
