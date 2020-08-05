"""add password_reset_string to person table

Revision ID: 8755cd559d65
Revises: 0bf05df57eec
Create Date: 2020-07-29 23:44:38.049231

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8755cd559d65'
down_revision = '0bf05df57eec'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("person") as batch_op:
        batch_op.add_column(sa.Column('password_reset_string', sa.String(), nullable=True))

def downgrade():
    pass
