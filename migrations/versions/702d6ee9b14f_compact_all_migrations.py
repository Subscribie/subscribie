"""compact all migrations

Revision ID: 702d6ee9b14f
Revises:
Create Date: 2020-09-21 21:11:08.854792

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "702d6ee9b14f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "choice_group" not in tables:
        op.create_table(
            "choice_group",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("title", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "company" not in tables:
        op.create_table(
            "company",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("name", sa.String(255), nullable=True),
            sa.Column("slogan", sa.String(255), nullable=True),
            sa.Column("logo_src", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "email_template" not in tables:
        op.create_table(
            "email_template",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("custom_welcome_email_template", sa.String(255), nullable=True),
            sa.Column("use_custom_welcome_email", sa.Boolean(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "integration" not in tables:
        op.create_table(
            "integration",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("google_tag_manager_active", sa.Boolean(), nullable=True),
            sa.Column("google_tag_manager_container_id", sa.String(255), nullable=True),
            sa.Column("tawk_active", sa.Boolean(), nullable=True),
            sa.Column("tawk_property_id", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "module" not in tables:
        op.create_table(
            "module",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("name", sa.String(255), nullable=True),
            sa.Column("src", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "module_seo_page_title" not in tables:
        op.create_table(
            "module_seo_page_title",
            sa.Column("path", sa.String(255), nullable=False),
            sa.Column("title", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("path"),
        )

    if "module_style" not in tables:
        op.create_table(
            "module_style",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("css", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "page" not in tables:
        op.create_table(
            "page",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("page_name", sa.String(255), nullable=True),
            sa.Column("path", sa.String(255), nullable=True),
            sa.Column("template_file", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "payment_provider" not in tables:
        op.create_table(
            "payment_provider",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("gocardless_active", sa.Boolean(), nullable=True),
            sa.Column("gocardless_access_token", sa.String(255), nullable=True),
            sa.Column("gocardless_environment", sa.String(255), nullable=True),
            sa.Column("stripe_active", sa.Boolean(), nullable=True),
            sa.Column("stripe_publishable_key", sa.String(255), nullable=True),
            sa.Column("stripe_secret_key", sa.String(255), nullable=True),
            sa.Column("stripe_webhook_endpoint_secret", sa.String(255), nullable=True),
            sa.Column("stripe_webhook_endpoint_id", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "person" not in tables:
        op.create_table(
            "person",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("uuid", sa.String(255), nullable=True),
            sa.Column("sid", sa.String(255), nullable=True),
            sa.Column("ts", sa.DateTime(), nullable=True),
            sa.Column("given_name", sa.String(255), nullable=True),
            sa.Column("family_name", sa.String(255), nullable=True),
            sa.Column("address_line1", sa.String(255), nullable=True),
            sa.Column("city", sa.String(255), nullable=True),
            sa.Column("postal_code", sa.String(255), nullable=True),
            sa.Column("email", sa.String(255), nullable=True),
            sa.Column("password", sa.String(255), nullable=True),
            sa.Column("password_reset_string", sa.String(255), nullable=True),
            sa.Column("mobile", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "plan" not in tables:
        op.create_table(
            "plan",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("archived", sa.Boolean(), nullable=True),
            sa.Column("uuid", sa.String(255), nullable=True),
            sa.Column("title", sa.String(255), nullable=True),
            sa.Column("interval_unit", sa.String(255), nullable=True),
            sa.Column("interval_amount", sa.Integer(), nullable=True),
            sa.Column("monthly_price", sa.Integer(), nullable=True),
            sa.Column("sell_price", sa.Integer(), nullable=True),
            sa.Column("days_before_first_charge", sa.Integer(), nullable=True),
            sa.Column("primary_icon", sa.String(255), nullable=True),
            sa.Column("position", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "setting" not in tables:
        op.create_table(
            "setting",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("reply_to_email_address", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "user" not in tables:
        op.create_table(
            "user",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("email", sa.String(255), nullable=True),
            sa.Column("password", sa.String(255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("active", sa.String(255), nullable=True),
            sa.Column("login_token", sa.String(255), nullable=True),
            sa.Column("password_reset_string", sa.String(255), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if "option" not in tables:
        op.create_table(
            "option",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("choice_group_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("title", sa.String(255), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("primary_icon", sa.String(255), nullable=True),
            sa.ForeignKeyConstraint(
                ["choice_group_id"],
                ["choice_group.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "plan_choice_group" not in tables:
        op.create_table(
            "plan_choice_group",
            sa.Column("choice_group_id", sa.Integer(), nullable=True),
            sa.Column("plan_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["choice_group_id"],
                ["choice_group.id"],
            ),
            sa.ForeignKeyConstraint(
                ["plan_id"],
                ["plan.id"],
            ),
        )

    if "plan_requirements" not in tables:
        op.create_table(
            "plan_requirements",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("plan_id", sa.Integer(), nullable=True),
            sa.Column("instant_payment", sa.Boolean(), nullable=True),
            sa.Column("subscription", sa.Boolean(), nullable=True),
            sa.Column("note_to_seller_required", sa.Boolean(), nullable=True),
            sa.Column("note_to_buyer_message", sa.String(255), nullable=True),
            sa.ForeignKeyConstraint(
                ["plan_id"],
                ["plan.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "plan_selling_points" not in tables:
        op.create_table(
            "plan_selling_points",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("point", sa.String(255), nullable=True),
            sa.Column("plan_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["plan_id"],
                ["plan.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "subscription" not in tables:
        op.create_table(
            "subscription",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("uuid", sa.String(255), nullable=True),
            sa.Column("sku_uuid", sa.String(255), nullable=True),
            sa.Column("gocardless_subscription_id", sa.String(255), nullable=True),
            sa.Column("person_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(
                ["person_id"],
                ["person.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "chosen_option" not in tables:
        op.create_table(
            "chosen_option",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("choice_group_id", sa.Integer(), nullable=True),
            sa.Column("choice_group_title", sa.String(255), nullable=True),
            sa.Column("option_title", sa.String(255), nullable=True),
            sa.Column("subscription_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["subscription_id"],
                ["subscription.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "subscription_note" not in tables:
        op.create_table(
            "subscription_note",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("note", sa.String(255), nullable=True),
            sa.Column("subscription_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(
                ["subscription_id"],
                ["subscription.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if "transactions" not in tables:
        op.create_table(
            "transactions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("uuid", sa.String(255), nullable=True),
            sa.Column("amount", sa.Integer(), nullable=True),
            sa.Column("comment", sa.Text(), nullable=True),
            sa.Column("external_id", sa.String(255), nullable=True),
            sa.Column("external_src", sa.String(255), nullable=True),
            sa.Column("person_id", sa.Integer(), nullable=True),
            sa.Column("subscription_id", sa.Integer(), nullable=True),
            sa.Column("payment_status", sa.String(255), nullable=True),
            sa.Column("fulfillment_state", sa.String(255), nullable=True),
            sa.ForeignKeyConstraint(
                ["person_id"],
                ["person.id"],
            ),
            sa.ForeignKeyConstraint(
                ["subscription_id"],
                ["subscription.id"],
            ),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade():
    pass
