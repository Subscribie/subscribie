"""add payment_provider table

Revision ID: 252d0418696b
Revises: 9dd0f253a79f
Create Date: 2020-05-30 14:33:45.490826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '252d0418696b'
down_revision = '9dd0f253a79f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('payment_provider',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('gocardless_active', sa.Boolean(), nullable=True),
    sa.Column('gocardless_access_token', sa.String(), nullable=True),
    sa.Column('gocardless_environment', sa.String(), nullable=True),
    sa.Column('stripe_active', sa.Boolean(), nullable=True),
    sa.Column('stripe_publishable_key', sa.String(), nullable=True),
    sa.Column('stripe_secret_key', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('payment_provider')
