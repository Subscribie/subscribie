"""create plan_requirements plan fk

Revision ID: b6d224b6e151
Revises: c4bf5f252696
Create Date: 2020-08-03 18:22:32.016096

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b6d224b6e151'
down_revision = 'c4bf5f252696'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan_requirements") as batch_op:
        batch_op.create_foreign_key('fk_plan', 'plan', ['plan_id'], ['id'])

def downgrade():
    pass
