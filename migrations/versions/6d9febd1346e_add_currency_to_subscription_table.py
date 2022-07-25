"""add currency to Subscription table

Revision ID: 6d9febd1346e
Revises: 6738e7241978
Create Date: 2022-07-25 22:01:11.062099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d9febd1346e'
down_revision = '6738e7241978'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch_op:
        batch_op.add_column(sa.Column('currency', sa.String(), default="USD"))

def downgrade():
    pass
