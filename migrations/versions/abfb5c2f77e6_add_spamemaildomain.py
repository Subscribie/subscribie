"""add SpamEmailDomain

Revision ID: abfb5c2f77e6
Revises: abc1ff0c85e0
Create Date: 2024-11-11 21:27:48.094799

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "abfb5c2f77e6"
down_revision = "abc1ff0c85e0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "spam_email_domain",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(), nullable=True),
        sa.Column("ts", sa.DateTime(), nullable=True),
        sa.Column("domain", sa.String(), nullable=True),
        sa.Column("archived", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    pass
