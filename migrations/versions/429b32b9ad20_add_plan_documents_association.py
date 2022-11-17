"""add plan documents association

Revision ID: 429b32b9ad20
Revises: fc7ac6f06521
Create Date: 2022-11-17 01:07:18.115335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "429b32b9ad20"
down_revision = "fc7ac6f06521"
branch_labels = None
depends_on = None


def upgrade():
    """
    Ability to link plan->documents
    and document->plans
    Many to many relationship.
    """
    op.create_table(
        "plan_document_associations",
        sa.Column("plan_uuid", sa.Integer(), nullable=False),
        sa.Column("document_uuid", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["document_uuid"],
            ["document.uuid"],
        ),
        sa.ForeignKeyConstraint(
            ["plan_uuid"],
            ["plan.uuid"],
        ),
    )


def downgrade():
    pass
