"""plan_requirements_fk_plan
Revision ID: d0475c520f1e
Revises: ddff11d33adb
Create Date: 2020-08-03 16:29:55.218843
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, INTEGER


# revision identifiers, used by Alembic.
revision = 'd0475c520f1e'
down_revision = 'ddff11d33adb'
branch_labels = None
depends_on = None


def upgrade():
    # Create and drop empty item table to satisfy dangling foriegn key           
    # references                                                                 

    naming_convention = {
    "fk":
    "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
    with op.batch_alter_table("plan_requirements", naming_convention=naming_convention) as batch_op:
        batch_op.drop_constraint('fk_plan_requirements_plan_id_item', type_='foreignkey')

    op.drop_table("item")

def downgrade():
    pass

