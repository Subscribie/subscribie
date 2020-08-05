"""create asociation table ChoiceGroup Option

Revision ID: 69199ce31c96
Revises: 249447f92c51
Create Date: 2020-08-05 16:30:36.959739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69199ce31c96'
down_revision = '249447f92c51'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'plan_choice_group',
        sa.Column('choice_group_id', sa.Integer, sa.ForeignKey('choice_group.id')),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('plan.id'))
    )


def downgrade():
    pass
