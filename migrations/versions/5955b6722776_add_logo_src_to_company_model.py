"""add logo_src to Company model

Revision ID: 5955b6722776
Revises: 488a43188009
Create Date: 2020-09-12 13:50:20.230961

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5955b6722776'
down_revision = '488a43188009'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("company") as batch_op:
        batch_op.add_column(sa.Column('logo_src', sa.String()))


def downgrade():
    pass
