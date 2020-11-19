from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil.relativedelta import relativedelta

from .database import database


def uuid_string():
    return str(uuid4())


class User(database.Model):
    __tablename__ = "user"
    id = database.Column(database.Integer(), primary_key=True)
    email = database.Column(database.String())
    password = database.Column(database.String())
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    active = database.Column(database.String)
    login_token = database.Column(database.String)
    password_reset_string = database.Column(database.String())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.email)


class Person(database.Model):
    __tablename__ = "person"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    sid = database.Column(database.String())
    ts = database.Column(database.DateTime, default=datetime.utcnow)
    given_name = database.Column(database.String())
    family_name = database.Column(database.String())
    address_line1 = database.Column(database.String())
    city = database.Column(database.String())
    postal_code = database.Column(database.String())
    email = database.Column(database.String())
    password = database.Column(database.String())  # Hash of password
    password_reset_string = database.Column(database.String())
    mobile = database.Column(database.String())
    subscriptions = relationship("Subscription", back_populates="person")
    transactions = relationship("Transaction", back_populates="person")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<Person {}>".format(self.given_name)


class Subscription(database.Model):
    __tablename__ = "subscription"
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=uuid_string)
    sku_uuid = database.Column(database.String())
    gocardless_subscription_id = database.Column(database.String())
    person_id = database.Column(database.Integer(), ForeignKey("person.id"))
    plan = relationship(
        "Plan",
        uselist=False,
        primaryjoin="foreign(Plan.uuid)==Subscription.sku_uuid",  # noqa
    )
    person = relationship("Person", back_populates="subscriptions")
    note = relationship("SubscriptionNote", back_populates="subscription", uselist=False)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    transactions = relationship("Transaction", back_populates="subscription")
    chosen_options = relationship("ChosenOption", back_populates="subscription")
    subscribie_checkout_session_id = database.Column(database.String())

    def next_date(self):
        """Return the next delivery date of this subscription
        Based on the created_at date, divided by number of intervals since
        + days remaining.
        """
        from datetime import date
        from dateutil import rrule

        if self.plan.interval_unit == "yearly":
            next_date = list(
                rrule.rrule(
                    rrule.YEARLY,
                    interval=1,
                    until=date.today() + relativedelta(years=+2),
                    dtstart=self.created_at,
                )
            )[-1]
        elif self.plan.interval_unit == "weekly":
            next_date = list(
                rrule.rrule(
                    rrule.WEEKLY,
                    interval=1,
                    until=date.today() + relativedelta(weeks=+2),
                    dtstart=self.created_at,
                )
            )[-1]
        else:
            next_date = list(
                rrule.rrule(
                    rrule.MONTHLY,
                    interval=1,
                    until=date.today() + relativedelta(months=+2),
                    dtstart=self.created_at,
                )
            )[-1]

        return next_date


class SubscriptionNote(database.Model):
    __tablename__ = "subscription_note"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    note = database.Column(database.String())
    subscription_id = database.Column(
        database.Integer(), ForeignKey("subscription.id")
    )  # noqa
    subscription = relationship("Subscription", back_populates="note")


class Company(database.Model):
    __tablename__ = "company"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    name = database.Column(database.String())
    slogan = database.Column(database.String())
    logo_src = database.Column(database.String())


association_table_plan_choice_group = database.Table(
    "plan_choice_group",
    database.Column("choice_group_id", database.Integer, ForeignKey("choice_group.id")),
    database.Column("plan_id", database.Integer, ForeignKey("plan.id")),
)


class Plan(database.Model):
    __tablename__ = "plan"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    archived = database.Column(database.Boolean(), default=False)
    uuid = database.Column(database.String(), default=uuid_string)
    title = database.Column(database.String())
    interval_unit = database.Column(database.String())  # Charge interval
    interval_amount = database.Column(
        database.Integer(), default=0
    )  # Charge amount each interval
    monthly_price = database.Column(database.Integer())
    sell_price = database.Column(database.Integer())  # Upfront price
    days_before_first_charge = database.Column(database.Integer(), default=0)
    primary_icon = database.Column(database.String())
    requirements = relationship(
        "PlanRequirements", uselist=False, back_populates="plan"
    )
    selling_points = relationship("PlanSellingPoints", back_populates="plan")
    choice_groups = relationship(
        "ChoiceGroup",
        secondary=association_table_plan_choice_group,
        backref=database.backref("plans", lazy="dynamic"),
    )
    position = database.Column(database.Integer(), default=0)


class PlanRequirements(database.Model):
    __tablename__ = "plan_requirements"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    plan_id = database.Column(database.Integer(), ForeignKey("plan.id"))
    plan = relationship("Plan", back_populates="requirements")
    instant_payment = database.Column(database.Boolean(), default=False)
    subscription = database.Column(database.Boolean(), default=False)
    note_to_seller_required = database.Column(database.Boolean(), default=False)  # noqa
    note_to_buyer_message = database.Column(database.String())


class PlanSellingPoints(database.Model):
    __tablename__ = "plan_selling_points"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    point = database.Column(database.String())
    plan_id = database.Column(database.Integer(), ForeignKey("plan.id"))
    plan = relationship("Plan", back_populates="selling_points")


class Integration(database.Model):
    __tablename__ = "integration"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    google_tag_manager_active = database.Column(database.Boolean())
    google_tag_manager_container_id = database.Column(database.String())
    tawk_active = database.Column(database.Boolean())
    tawk_property_id = database.Column(database.String())


class PaymentProvider(database.Model):
    __tablename__ = "payment_provider"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    gocardless_active = database.Column(database.Boolean())
    gocardless_access_token = database.Column(database.String())
    gocardless_environment = database.Column(database.String())
    stripe_active = database.Column(database.Boolean())
    stripe_live_webhook_endpoint_secret = database.Column(database.String())
    stripe_live_webhook_endpoint_id = database.Column(database.String())
    stripe_live_connect_account_id = database.Column(database.String())
    stripe_test_webhook_endpoint_secret = database.Column(database.String())
    stripe_test_webhook_endpoint_id = database.Column(database.String())
    stripe_test_connect_account_id = database.Column(database.String())
    stripe_livemode = database.Column(database.Boolean(), default=False)


class Page(database.Model):
    __tablename__ = "page"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    page_name = database.Column(database.String())
    path = database.Column(database.String())
    template_file = database.Column(database.String())
    private = database.Column(database.Boolean())


class Module(database.Model):
    __tablename__ = "module"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    name = database.Column(database.String())
    src = database.Column(database.String())


class Transaction(database.Model):
    __tablename__ = "transactions"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    amount = database.Column(database.Integer())
    comment = database.Column(database.Text())
    # External id e.g. Stripe or GoCardless id
    external_id = database.Column(database.String())
    # Source of transaction e.g. Stripe or GoCardless
    external_src = database.Column(database.String())
    person_id = database.Column(database.Integer(), ForeignKey("person.id"))
    person = relationship("Person", back_populates="transactions")
    subscription_id = database.Column(
        database.Integer(), ForeignKey("subscription.id")
    )  # noqa
    subscription = relationship("Subscription", back_populates="transactions")
    payment_status = database.Column(database.String())
    fulfillment_state = database.Column(database.String())


class SeoPageTitle(database.Model):
    __tablename__ = "module_seo_page_title"
    path = database.Column(database.String(), primary_key=True)
    title = database.Column(database.String())


class ChoiceGroup(database.Model):
    __tablename__ = "choice_group"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    title = database.Column(database.String())
    options = relationship("Option", back_populates="choice_group")


class Option(database.Model):
    __tablename__ = "option"
    id = database.Column(database.Integer(), primary_key=True)
    choice_group_id = database.Column(
        database.Integer(), ForeignKey("choice_group.id")
    )  # noqa
    choice_group = relationship("ChoiceGroup", back_populates="options")
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    title = database.Column(database.String())
    description = database.Column(database.Text())
    primary_icon = database.Column(database.String())


class ChosenOption(database.Model):
    __tablename__ = "chosen_option"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    choice_group_id = database.Column(database.Integer())
    choice_group_title = database.Column(database.String())
    option_title = database.Column(database.String())
    subscription_id = database.Column(
        database.Integer(), ForeignKey("subscription.id")
    )  # noqa
    subscription = relationship("Subscription", back_populates="chosen_options")  # noqa


class ModuleStyle(database.Model):
    """For custom css style injection"""

    __tablename__ = "module_style"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    css = database.Column(database.String())


class EmailTemplate(database.Model):
    """Custom email templates"""

    __tablename__ = "email_template"
    id = database.Column(database.Integer(), primary_key=True)
    custom_welcome_email_template = database.Column(database.String())
    use_custom_welcome_email = database.Column(
        database.Boolean(), default=False
    )  # noqa


class Setting(database.Model):
    """Settings"""

    __tablename__ = "setting"
    id = database.Column(database.Integer(), primary_key=True)
    reply_to_email_address = database.Column(database.String())


class File(database.Model):
    """File uploads meta"""

    __tablename__ = "file"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    file_name = database.Column(database.String())
