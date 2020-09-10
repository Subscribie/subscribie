"""add positionto Plan model

Revision ID: 488a43188009
Revises: 38dad517daf6
Create Date: 2020-09-10 14:43:05.201039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '488a43188009'
down_revision = '38dad517daf6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column('position', sa.Integer(), default=0))


def downgrade():
    pass
