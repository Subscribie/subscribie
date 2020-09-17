"""add setting model

Revision ID: db265b2a50e1
Revises: b9b71ddd39c1
Create Date: 2020-09-17 22:23:51.181362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db265b2a50e1'
down_revision = 'b9b71ddd39c1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('setting',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('reply_to_email_address', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
