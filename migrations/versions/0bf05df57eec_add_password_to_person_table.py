"""add password to person table

Revision ID: 0bf05df57eec
Revises: 9624c9410a7a
Create Date: 2020-07-29 18:40:01.376381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bf05df57eec'
down_revision = '9624c9410a7a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('person') as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(), nullable=True))

def downgrade():
    pass
