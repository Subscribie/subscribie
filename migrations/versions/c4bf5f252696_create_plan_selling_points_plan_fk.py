"""create plan_selling_points plan fk

Revision ID: c4bf5f252696
Revises: 146b0453e9b8
Create Date: 2020-08-03 18:15:29.171108

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c4bf5f252696'
down_revision = '146b0453e9b8'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan_selling_points") as batch_op:
        batch_op.create_foreign_key('fk_plan', 'plan', ['plan_id'], ['id'])

def downgrade():
    pass
