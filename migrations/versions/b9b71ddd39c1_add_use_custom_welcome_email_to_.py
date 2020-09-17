"""add use_custom_welcome_email to EmailTemplate model

Revision ID: b9b71ddd39c1
Revises: 67b3424ccacc
Create Date: 2020-09-17 14:34:34.834093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9b71ddd39c1'
down_revision = '67b3424ccacc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('email_template') as batch_op:
        batch_op.add_column(sa.Column('use_custom_welcome_email', sa.Boolean(), default=False))


def downgrade():
    pass
