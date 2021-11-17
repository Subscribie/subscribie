"""create upcoming invoice table

Revision ID: 3a8f3089d09d
Revises: c48dccfb0df5
Create Date: 2021-05-31 21:24:34.681376

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3a8f3089d09d"
down_revision = "c48dccfb0df5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "upcoming_invoice",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True),
        sa.Column("stripe_invoice_status", sa.String(255), nullable=True),
        sa.Column("stripe_amount_due", sa.String(255), nullable=True),
        sa.Column("stripe_amount_paid", sa.String(255), nullable=True),
        sa.Column("stripe_currency", sa.String(255), nullable=True),
        sa.Column("stripe_next_payment_attempt", sa.String(255), nullable=True),
        sa.Column("subscription_uuid", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subscription_uuid"],
            ["subscription.uuid"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
