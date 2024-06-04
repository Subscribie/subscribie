"""add answer model

Revision ID: c70cd4900c96
Revises: 063ddc60bef1
Create Date: 2024-05-14 21:18:13.745275

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c70cd4900c96"
down_revision = "063ddc60bef1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "answer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("question_id", sa.Integer(), nullable=True),
        sa.Column("question_title", sa.String(), nullable=True),
        sa.Column("response", sa.String(), nullable=True),
        sa.Column("subscription_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscription.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
