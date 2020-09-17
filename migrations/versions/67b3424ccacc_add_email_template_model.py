"""add email_template model

Revision ID: 67b3424ccacc
Revises: 5955b6722776
Create Date: 2020-09-16 17:36:31.123382

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67b3424ccacc'
down_revision = '5955b6722776'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('email_template',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('custom_welcome_email_template', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    pass
