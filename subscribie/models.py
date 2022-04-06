import logging
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import ForeignKey
from sqlalchemy import event
from sqlalchemy import Column
from sqlalchemy import Boolean


from datetime import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil.relativedelta import relativedelta
from flask import request, current_app
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account_id,
    stripe_invoice_failed,
    stripe_invoice_failing,
    get_stripe_invoices,
)
import stripe
import json

from .database import database

log = logging.getLogger(__name__)


@event.listens_for(database.session, "do_orm_execute")
def _do_orm_execute_hide_archived(orm_execute_state):
    if (
        orm_execute_state.is_select
        and not orm_execute_state.is_column_load
        and not orm_execute_state.is_relationship_load
        and not orm_execute_state.execution_options.get("include_archived", False)
    ):
        orm_execute_state.statement = orm_execute_state.statement.options(
            with_loader_criteria(
                HasArchived,
                lambda cls: cls.archived == False,  # noqa: E712
                include_aliases=True,
            )
        )


@event.listens_for(Query, "before_compile", retval=True, bake_ok=True)
def filter_archived(query):
    for desc in query.column_descriptions:
        entity = desc["entity"]
        if desc["type"] is Person and "archived-subscribers" in request.path:
            query = query.filter(entity.archived == 1)
            return query
        elif (
            desc["type"] is Person
            and request.path != "/"
            and "un-archive" not in request.path
            and "/account/login" not in request.path
            and "/auth/login" not in request.path
            and "/account/forgot-password" not in request.path
            and "account/password-reset" not in request.path
            and "/account" not in request.path
            and "/admin/transactions" not in request.path
            and "/static" not in request.path
            and "/admin/dashboard" not in request.path
            and "/page" not in request.path
            and "/new_customer" not in request.path
            and "/start-building" not in request.path
            and "/order-summary" not in request.path
            and "/stripe-create-checkout-session" not in request.path
            and "instant_payment_complete" not in request.path
            and "thankyou" not in request.path
        ):
            query = query.filter(entity.archived == 0)
            return query


def uuid_string():
    return str(uuid4())


class HasArchived(object):
    """Mixin that identifies a class as having archived entities"""

    archived = Column(Boolean, nullable=False, default=0)


class User(database.Model):
    __tablename__ = "user"
    id = database.Column(database.Integer(), primary_key=True)
    email = database.Column(database.String())
    password = database.Column(database.String())
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    active = database.Column(database.String)
    login_token = database.Column(database.String)
    password_reset_string = database.Column(database.String())
    password_expired = database.Column(database.Boolean(), default=0)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<User {}>".format(self.email)


class Person(database.Model, HasArchived):
    __tablename__ = "person"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    sid = database.Column(database.String())
    ts = database.Column(database.DateTime, default=datetime.utcnow)
    given_name = database.Column(database.String())
    family_name = database.Column(database.String())
    full_name = database.column_property(given_name + " " + family_name)
    address_line1 = database.Column(database.String())
    city = database.Column(database.String())
    postal_code = database.Column(database.String())
    email = database.Column(database.String())
    password = database.Column(database.String())  # Hash of password
    password_reset_string = database.Column(database.String())
    password_expired = database.Column(database.Boolean(), default=1)
    mobile = database.Column(database.String())
    subscriptions = relationship("Subscription", back_populates="person")
    transactions = relationship("Transaction", back_populates="person")

    def invoices(self, refetchCachedStripeInvoices=False):
        """Get all cached Stripe invoices for a given person

        NOTE: This is a **cached** view of Stripe invoices,
        to refresh and get the latest Stripe invoices, set refetchCachedStripeInvoices
        to True.

        NOTE: a person may have zero or more subscriptions,
        with each subscription having zero or more invoices

        For Stripe invoices, the stripe customer id is needed,
        note it is possible (though rare) for one Subscribie customer id
        to have multiple Stripe customer ids. This is not as issue
        since we store the Stripe subscription id, and, if needed, can
        query the Stripe customer id from the Subscription object.
        See:
        - this file class "Subscription" with colum "stripe_subscription_id"
        - https://stripe.com/docs/api/subscriptions/object?lang=python#subscription_object-customer # noqa: E501
        """
        if refetchCachedStripeInvoices:
            # TODO optimise to only refetch invoices for this Subscriber
            get_stripe_invoices(app=current_app)

        stripe.api_key = get_stripe_secret_key()
        stripe_account_id = get_stripe_connect_account_id()
        query = database.session.query(StripeInvoice)
        query = query.join(
            Subscription, StripeInvoice.subscribie_subscription_id == Subscription.id
        )
        query = query.join(Person, Subscription.person_id == Person.id)
        query = query.filter(Person.id == self.id)
        invoices = query.all()
        for invoice in invoices:
            stripeRawInvoice = json.loads(invoice.stripe_invoice_raw_json)
            setattr(
                invoice,
                "created",
                stripeRawInvoice["created"],
            )
            # Get stripe_decline_code if possible
            try:
                payment_intent_id = stripeRawInvoice["payment_intent"]
                stripe_decline_code = stripe.PaymentIntent.retrieve(
                    payment_intent_id,
                    stripe_account=stripe_account_id,
                ).last_payment_error.decline_code
                setattr(invoice, "stripe_decline_code", stripe_decline_code)
            except Exception as e:
                log.debug(
                    f"Failed to get stripe_decline_code for invoice {invoice.id}. Exeption: {e}"  # noqa: E501
                )
            # Get next payment attempt date if possible
            try:
                next_payment_attempt = stripeRawInvoice["next_payment_attempt"]
                setattr(invoice, "next_payment_attempt", next_payment_attempt)
            except Exception as e:
                log.debug(
                    f"Failed to get sripe next_payment_attempt for invoice {invoice.id}. Exeption: {e}"  # noqa: E501
                )

        return invoices

    def failed_invoices(self):
        """List Subscribers failed invoices"""
        failed_invoices = []
        invoices = self.invoices()
        for invoice in invoices:
            if stripe_invoice_failed(invoice):
                failed_invoices.append(invoice)
        return failed_invoices

    def failing_invoices(self):
        """List Subscribers failed invoices"""
        failing_invoices = []
        invoices = self.invoices()
        for invoice in invoices:
            if stripe_invoice_failing(invoice):
                failing_invoices.append(invoice)
        return failing_invoices

    def bad_invoices(self):
        """List Subscribers failing and failed invoices"""
        bad_invoices = []
        invoices = self.invoices()
        for invoice in invoices:
            if stripe_invoice_failed(invoice) or stripe_invoice_failing(invoice):
                bad_invoices.append(invoice)
        return bad_invoices

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return "<Person {}>".format(self.given_name)


class Balance(database.Model):
    __tablename__ = "balance"
    uuid = database.Column(database.String(), default=uuid_string, primary_key=True)
    available_amount = database.Column(database.Integer(), nullable=True)
    available_currency = database.Column(database.String(), nullable=True)
    stripe_livemode = database.Column(database.Boolean(), default=False)


class LoginToken(database.Model):
    __tablename__ = "login_token"
    user_uuid = database.Column(database.String, primary_key=True)
    login_token = database.Column(database.String)


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
    upcoming_invoice = relationship(
        "UpcomingInvoice", back_populates="subscription", uselist=False
    )
    note = relationship(
        "SubscriptionNote", back_populates="subscription", uselist=False
    )

    # List of associated Stripe Invoices (may not be live synced)
    stripe_invoices = relationship("StripeInvoice")
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    transactions = relationship("Transaction", back_populates="subscription")
    chosen_options = relationship("ChosenOption", back_populates="subscription")
    subscribie_checkout_session_id = database.Column(database.String())
    stripe_subscription_id = database.Column(database.String())
    stripe_external_id = database.Column(database.String())
    stripe_status = database.Column(database.String())
    # stripe_cancel_at is the 'live' setting (which may change)
    # and must be checked via cron/webhooks. Plan.cancel_at allows
    # a shop owner to set a cancel_at date before subscribers sign-up,
    # which creates subscriptions.
    stripe_cancel_at = database.Column(database.Integer(), default=0)
    stripe_pause_collection = database.Column(database.String())

    def stripe_subscription_active(self):
        if self.stripe_subscription_id is not None:
            if self.stripe_status == "active":
                return True
        return False

    def next_date(self):
        """Return the next delivery date of this subscription
        Based on the created_at date, divided by number of intervals since
        + days remaining.
        """
        from datetime import datetime
        from dateutil import rrule

        if self.plan.interval_unit == "yearly":
            next_date = list(
                rrule.rrule(
                    rrule.YEARLY,
                    interval=1,
                    until=datetime.utcnow() + relativedelta(years=+1),
                    dtstart=self.created_at,
                )
            )[-1]
        elif self.plan.interval_unit == "weekly":
            next_date = list(
                rrule.rrule(
                    rrule.WEEKLY,
                    interval=1,
                    until=datetime.utcnow() + relativedelta(weeks=+1),
                    dtstart=self.created_at,
                )
            )[-1]
        else:
            next_date = list(
                rrule.rrule(
                    rrule.MONTHLY,
                    interval=1,
                    until=datetime.utcnow() + relativedelta(months=+1),
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


class UpcomingInvoice(database.Model):
    """
    A temporary view of upcoming invoices.

    The keys in this table must not be relied upon.
    Entries in this table are *removed* and fetched again by
    subscribie.invoice.fetch_stripe_upcoming_invoices

    Requires syncing with stripe api as invoices transition
    to paid (or failed).
    """

    __tablename__ = "upcoming_invoice"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    # Note, upcoming invoices do not have an id https://stripe.com/docs/api/invoices/upcoming # noqa
    stripe_subscription_id = database.Column(database.String())
    stripe_invoice_status = database.Column(database.String())
    stripe_amount_due = database.Column(database.String())
    stripe_amount_paid = database.Column(database.String())
    stripe_currency = database.Column(database.String())
    stripe_next_payment_attempt = database.Column(database.String())
    subscription_uuid = database.Column(
        database.Integer, ForeignKey("subscription.uuid")
    )
    subscription = relationship("Subscription", back_populates="upcoming_invoice")


class StripeInvoice(database.Model):
    """
    Reflection of Stripe Invoices

    Not a live in-sync view of Stripe created invoices

    Purpose: To reduce round trip time fetching invoice information
    from Stripe each time (cache).

    Note: not all invoices have to originate from Stripe,
          this models table name is named stripe_invoice for
          that reason.

    Note: Inserts are upsert-ed to preserve keys
    """

    __tablename__ = "stripe_invoice"
    uuid = database.Column(database.String(), default=uuid_string, primary_key=True)
    id = database.Column(database.String(), nullable=True)
    status = database.Column(database.String(), nullable=True)
    amount_due = database.Column(database.Integer(), nullable=True)
    amount_paid = database.Column(database.Integer(), nullable=True)
    amount_remaining = database.Column(database.Integer(), nullable=True)
    application_fee_amount = database.Column(database.Integer(), nullable=True)
    attempt_count = database.Column(database.Integer(), nullable=True)
    billing_reason = database.Column(database.String(), nullable=True)
    collection_method = database.Column(database.String(), nullable=True)
    currency = database.Column(database.String(), nullable=True)
    next_payment_attempt = database.Column(database.Integer(), nullable=True)
    stripe_subscription_id = database.Column(database.String(), nullable=True)
    subscribie_subscription_id = database.Column(
        database.Integer(), ForeignKey("subscription.id"), nullable=True
    )
    subscribie_subscription = relationship(
        "Subscription", back_populates="stripe_invoices"
    )
    stripe_invoice_raw_json = database.Column(database.JSON(), nullable=True)


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


class Plan(database.Model, HasArchived):
    __tablename__ = "plan"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    title = database.Column(database.String())
    description = database.Column(database.String())
    interval_unit = database.Column(database.String())  # Charge interval
    interval_amount = database.Column(
        database.Integer(), default=0
    )  # Charge amount each interval
    monthly_price = database.Column(database.Integer())
    sell_price = database.Column(database.Integer())  # Upfront price
    days_before_first_charge = database.Column(database.Integer(), default=0)
    trial_period_days = database.Column(database.Integer(), default=0)
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

    category_uuid = database.Column(database.Integer, ForeignKey("category.uuid"))
    category = relationship("Category", back_populates="plans")
    private = database.Column(database.Boolean(), default=0)
    cancel_at = database.Column(database.Integer(), default=0)


class Category(database.Model):
    __tablename__ = "category"
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=uuid_string)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    name = database.Column(database.String())
    plans = relationship("Plan", back_populates="category")
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
    private = database.Column(database.Boolean(), default=0)


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
    external_refund_id = database.Column(database.String())
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
    css_properties_json = database.Column(database.String())
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
    charge_vat = database.Column(database.Boolean(), default=False)
    custom_code = database.Column(database.String(), default=None)
    shop_activated = database.Column(database.Boolean(), default=False)
    api_key_secret_live = database.Column(database.String(), default=None)
    api_key_secret_test = database.Column(database.String(), default=None)


class File(database.Model):
    """File uploads meta"""

    __tablename__ = "file"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    file_name = database.Column(database.String())


class TaxRate(database.Model):
    """Stripe Tax Rate ids"""

    __tablename__ = "tax_rate"
    id = database.Column(database.Integer(), primary_key=True)
    stripe_tax_rate_id = database.Column(database.String())
    stripe_livemode = database.Column(database.Boolean())
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
