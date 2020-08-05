"""rename plan_requirements.item_id to plan_id

Revision ID: ddff11d33adb
Revises: 4fd3a620b62e
Create Date: 2020-08-03 16:27:19.192208

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, INTEGER


# revision identifiers, used by Alembic.
revision = 'ddff11d33adb'
down_revision = '4fd3a620b62e'
branch_labels = None
depends_on = None

def upgrade():
    # Create and drop empty item table to satisfy dangling foriegn key 
    # references
    op.create_table(
        'item',
        Column('id', INTEGER, primary_key=True),
    )

    with op.batch_alter_table("plan_requirements") as batch_op:
        batch_op.alter_column("item_id", new_column_name="plan_id")

    op.drop_table("item")

def downgrade():                                                                 
    with op.batch_alter_table("plan_requirements") as batch_op:                  
        batch_op.alter_column("plan_id", new_column_name="item_id") 
