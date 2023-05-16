"""adding_is_donation_in_transaction_table

Revision ID: 94790e701430
Revises: bd63fd27d653
Create Date: 2023-03-02 19:45:02.205558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "94790e701430"
down_revision = "bd63fd27d653"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("transactions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_donation", sa.Boolean(), nullable=True))


def downgrade():
    pass
