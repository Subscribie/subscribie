"""add external_refund_id to transaction model

Revision ID: c751fe53a042
Revises: b767faeb4c0d
Create Date: 2021-04-08 15:19:14.355699

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c751fe53a042'
down_revision = 'b767faeb4c0d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('transactions') as batch_op:
        batch_op.add_column(sa.Column('external_refund_id', sa.String(255), nullable=True))

def downgrade():
    pass
