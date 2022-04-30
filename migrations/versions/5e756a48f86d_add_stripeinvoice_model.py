"""add StripeInvoice model

Revision ID: 5e756a48f86d
Revises: 89b4e5e02eac
Create Date: 2022-02-26 23:05:31.976561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5e756a48f86d"
down_revision = "89b4e5e02eac"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "stripe_invoice",
        sa.Column("uuid", sa.String(), nullable=False),
        sa.Column("id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("amount_due", sa.Integer(), nullable=True),
        sa.Column("amount_paid", sa.Integer(), nullable=True),
        sa.Column("amount_remaining", sa.Integer(), nullable=True),
        sa.Column("application_fee_amount", sa.Integer(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=True),
        sa.Column("billing_reason", sa.String(), nullable=True),
        sa.Column("collection_method", sa.String(), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("next_payment_attempt", sa.Integer(), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
        sa.Column("subscribie_subscription_id", sa.Integer(), nullable=True),
        sa.Column("stripe_invoice_raw_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subscribie_subscription_id"],
            ["subscription.id"],
        ),
        sa.PrimaryKeyConstraint("uuid"),
    )


def downgrade():
    pass
