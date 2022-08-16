"""add stripe_connect_account_id to PaymentProvider model

Revision ID: 3abcbb0428ef
Revises: 790aae5a7013
Create Date: 2020-09-23 17:17:30.127947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3abcbb0428ef"
down_revision = "790aae5a7013"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("payment_provider") as batch_op:
        batch_op.add_column(
            sa.Column("stripe_connect_account_id", sa.String(255), nullable=True)
        )


def downgrade():
    pass
