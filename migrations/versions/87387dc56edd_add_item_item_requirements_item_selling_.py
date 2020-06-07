"""add item, item_requirements, item_selling_points tables

Revision ID: 87387dc56edd
Revises: 36b57075d761
Create Date: 2020-05-24 22:56:49.814257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87387dc56edd'
down_revision = '36b57075d761'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('archived', sa.Boolean(), nullable=True),
    sa.Column('uuid', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('monthly_price', sa.Integer(), nullable=True),
    sa.Column('sell_price', sa.Integer(), nullable=True),
    sa.Column('days_before_first_charge', sa.Integer(), nullable=True),
    sa.Column('primary_icon', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_requirements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('instant_payment', sa.Boolean(), nullable=True),
    sa.Column('subscription', sa.Boolean(), nullable=True),
    sa.Column('note_to_seller_required', sa.Boolean(), nullable=True),
    sa.Column('note_to_buyer_message', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_selling_points',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('point', sa.String(), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('item_selling_points')
    op.drop_table('item_requirements')
    op.drop_table('item')
