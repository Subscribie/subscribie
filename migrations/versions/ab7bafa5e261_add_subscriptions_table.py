"""add subscriptions table

Revision ID: ab7bafa5e261
Revises: c01359894f1d
Create Date: 2020-04-24 20:51:55.535224

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab7bafa5e261'
down_revision = 'c01359894f1d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(), nullable=True),
    sa.Column('sku_uuid', sa.String(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('subscription')
