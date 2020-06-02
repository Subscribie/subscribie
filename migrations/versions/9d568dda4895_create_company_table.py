"""create company table

Revision ID: 9d568dda4895
Revises: cce32bb4e5f9
Create Date: 2020-06-02 22:17:18.937030

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = '9d568dda4895'
down_revision = 'cce32bb4e5f9'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()                                                         
    inspector = Inspector.from_engine(conn)                                      
    tables = inspector.get_table_names()
    
    if 'company' not in tables:
        op.create_table('company',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slogan', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    pass
