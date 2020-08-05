"""drop plan_selling_points item_id reference

Revision ID: 146b0453e9b8
Revises: d0475c520f1e
Create Date: 2020-08-03 18:04:57.458798

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, INTEGER


# revision identifiers, used by Alembic.
revision = '146b0453e9b8'
down_revision = 'd0475c520f1e'
branch_labels = None
depends_on = None


def upgrade():

    # Create and drop empty item table to satisfy dangling foriegn key           
    # references                                                                 
    op.create_table(                                                             
        'item',                                                                  
        Column('id', INTEGER, primary_key=True),                                 
    )

    naming_convention = {                                                        
    "fk":                                                                        
    "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",               
    }                                                                            
    with op.batch_alter_table("plan_selling_points", naming_convention=naming_convention) as batch_op:
        batch_op.alter_column("item_id", new_column_name="plan_id")
        batch_op.drop_constraint('fk_plan_selling_points_item_id_item', type_='foreignkey')
        batch_op.create_foreign_key('fk_plan', 'plan', ['plan_id'], ['id'])

    op.drop_table("item")

def downgrade():
    pass
