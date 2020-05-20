"""empty message

Revision ID: 5be4d91c4db1
Revises: 3861ee069f02
Create Date: 2020-05-20 18:30:02.318336

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import INTEGER, ForeignKey

# revision identifiers, used by Alembic.
revision = '5be4d91c4db1'
down_revision = '3861ee069f02'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('subscription_note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('note', sa.String(), nullable=True),
    sa.Column('subscription_id', INTEGER, ForeignKey('subscription.id')),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('subscription_note')
