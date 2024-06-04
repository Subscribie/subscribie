import logging
from sqlalchemy.orm import relationship
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy import ForeignKey
from sqlalchemy import event
from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy import desc

from typing import Optional
import datetime
import pytz
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from dateutil.relativedelta import relativedelta
from flask import request, current_app
from flask_babel import _
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account_id,
    stripe_invoice_failed,
    stripe_invoice_failing,
    get_stripe_invoices,
    get_discount_code,
    get_geo_currency_symbol,
    get_geo_currency_code,
    currencyFormat,
)
import stripe
import json
from enum import Enum

from .database import database

log = logging.getLogger(__name__)


@event.listens_for(database.session, "do_orm_execute")
def _do_orm_execute_hide_archived(orm_execute_state):
    if (
        orm_execute_state.is_select
        and not orm_execute_state.is_column_load
        and not orm_execute_state.is_relationship_load
        and not orm_execute_state.execution_options.get(
            "include_archived", False
        )  # noqa: E501
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
            and "uploads" not in request.path
            and "document" not in request.path
        ):
            query = query.filter(entity.archived == 0)
            return query


def uuid_string():
    return str(uuid4())


class HasArchived(object):
    """Mixin that identifies a class as having archived entities"""

    archived = Column(Boolean, nullable=True, default=0)


class CreatedAt(object):
    """Mixin that identifies a class as having created_at entities"""

    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )


class HasReadOnly(object):
    """Mixin that identifies a class as having read_only boolean field"""

    read_only = Column(Boolean, nullable=False, default=0)


class User(database.Model):
    __tablename__ = "user"
    id = database.Column(database.Integer(), primary_key=True)
    email = database.Column(database.String())
    password = database.Column(database.String())
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
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
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    sid = database.Column(database.String())
    ts = database.Column(database.DateTime, default=datetime.datetime.now(datetime.UTC))
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

    def get_subscriptions(self, include_archived=True):
        subscriptions = (
            database.session.query(Subscription)
            .execution_options(include_archived=include_archived)
            .join(Person, Subscription.person_id == Person.id)
            .join(Plan, Subscription.sku_uuid == Plan.uuid)
            .join(PlanRequirements, Plan.id == PlanRequirements.plan_id)
            .where(Person.id == self.id)
            .order_by(Subscription.id.desc())
            .all()
        )

        return subscriptions

    def balance(self, skipFetchDeclineCode=False):
        """Return the customer balance
        Customer balance is the total charged - total collected over the lifetime
        of their account.
        """
        total_charged = 0
        total_collected = 0
        customer_balance = 0

        invoices = self.invoices(skipFetchDeclineCode=skipFetchDeclineCode)
        for invoice in invoices:
            total_charged += invoice.amount_due

        # Calculate total_collected by adding up all invoices amount_due,
        # minus any invoices which still have amounts remaining
        # (Warning: partial payments on invoices is ignored, since a subscriber
        # cannot currently partially pay their invoice anyway)
        for invoice in invoices:
            if invoice.amount_remaining == 0:
                total_collected += invoice.amount_due

        customer_balance = total_charged - total_collected

        return {
            "total_charged": total_charged,
            "total_collected": total_collected,
            "customer_balance": customer_balance,
        }

    def invoices(self, refetchCachedStripeInvoices=False, skipFetchDeclineCode=False):
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
        query = database.session.query(StripeInvoice).execution_options(
            include_archived=True
        )
        query = query.join(
            Subscription,
            StripeInvoice.subscribie_subscription_id == Subscription.id,  # noqa: E501
        )
        query = query.join(Person, Subscription.person_id == Person.id)
        query = query.filter(Person.id == self.id)
        invoices = query.all()
        for invoice in invoices:
            stripeRawInvoice = json.loads(invoice.stripe_invoice_raw_json)
            setattr(invoice, "created", stripeRawInvoice["created"])
            # Get stripe_decline_code if possible, ignoring paid invoices
            try:
                if (
                    skipFetchDeclineCode is not True
                    # No point checking decline_code of a paid invoice
                    and invoice.status != "paid"
                ):
                    payment_intent_id = stripeRawInvoice["payment_intent"]
                    stripe_decline_code = stripe.PaymentIntent.retrieve(
                        payment_intent_id,
                        stripe_account=stripe_account_id,
                    ).last_payment_error.decline_code
                    setattr(invoice, "stripe_decline_code", stripe_decline_code)
                else:
                    setattr(invoice, "stripe_decline_code", "unknown")

            except Exception as e:
                log.debug(
                    f"Failed to get stripe_decline_code for invoice {invoice.id}. Exeption: {e}"  # noqa: E501
                )
            # Get next payment attempt date if possible
            try:
                next_payment_attempt = invoice.next_payment_attempt
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

    def bad_invoices(self, skipFetchDeclineCode=False):
        """List Subscribers failing and failed invoices"""
        bad_invoices = []
        invoices = self.invoices(skipFetchDeclineCode=skipFetchDeclineCode)
        for invoice in invoices:
            if stripe_invoice_failed(invoice) or stripe_invoice_failing(
                invoice
            ):  # noqa: E501
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
    uuid = database.Column(
        database.String(), default=uuid_string, primary_key=True
    )  # noqa: E501
    available_amount = database.Column(database.Integer(), nullable=True)
    available_currency = database.Column(database.String(), nullable=True)
    stripe_livemode = database.Column(database.Boolean(), default=False)


class LoginToken(database.Model):
    __tablename__ = "login_token"
    user_uuid = database.Column(database.String, primary_key=True)
    login_token = database.Column(database.String)


# Track Documents at time of subscription creation
# Note these are kept and never altered, compared to
# association_table_plan_to_document which store live
# documents which may change prior to subscriptions
# being created.
#
# Worked example:
#
# When a subscription is created, any associated document(s)
# associated with the subscribed Plan, are coped entirely to
# another enty in Document table as a system of record,
# and linked to the associated subscription.
# Should the live Document(s) be updated/altered, then the
# saved & archived document(s) will be left intact, and attached
# the the Subscription.
association_table_subscription_to_document = database.Table(
    "subscription_document_associations",
    database.Column(
        "subscription_uuid",
        database.Integer,
        ForeignKey("subscription.uuid"),
        primary_key=True,
    ),
    database.Column(
        "document_uuid",
        database.Integer,
        ForeignKey("document.uuid"),
    ),
)


class Subscription(database.Model):
    __tablename__ = "subscription"
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=uuid_string)
    sku_uuid = database.Column(database.String())
    gocardless_subscription_id = database.Column(database.String())
    person_id = database.Column(database.Integer(), ForeignKey("person.id"))
    interval_unit = database.Column(database.String())  # Charge interval
    interval_amount = database.Column(
        database.Integer(), default=0
    )  # Charge amount each interval
    sell_price = database.Column(database.Integer())  # Upfront price
    plan = relationship(
        "Plan",
        uselist=False,
        primaryjoin="foreign(Plan.uuid)==Subscription.sku_uuid",  # noqa
    )
    person = relationship("Person", back_populates="subscriptions")
    documents = relationship(
        "Document", secondary=association_table_subscription_to_document
    )
    upcoming_invoice = relationship(
        "UpcomingInvoice", back_populates="subscription", uselist=False
    )
    note = relationship(
        "SubscriptionNote", back_populates="subscription", uselist=False
    )

    # List of associated Stripe Invoices (may not be live synced)
    stripe_invoices = relationship("StripeInvoice")
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    transactions = relationship("Transaction", back_populates="subscription")
    chosen_options = relationship(
        "ChosenOption", back_populates="subscription"
    )  # noqa: E501
    question_answers = relationship("Answer", back_populates="subscription")
    currency = database.Column(database.String(), default="USD")
    subscribie_checkout_session_id = database.Column(database.String())
    stripe_subscription_id = database.Column(database.String())
    stripe_external_id = database.Column(database.String())
    stripe_status = database.Column(database.String())
    stripe_ended_at = database.Column(database.Integer(), nullable=True)

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
        import datetime
        from dateutil import rrule

        if self.plan.interval_unit == "yearly":
            next_date = list(
                rrule.rrule(
                    rrule.YEARLY,
                    interval=1,
                    until=datetime.datetime.now(datetime.UTC) + relativedelta(years=+1),
                    dtstart=pytz.utc.localize(self.created_at),
                )
            )[-1]
        elif self.plan.interval_unit == "weekly":
            next_date = list(
                rrule.rrule(
                    rrule.WEEKLY,
                    interval=1,
                    until=datetime.datetime.now(datetime.UTC) + relativedelta(weeks=+1),
                    dtstart=pytz.utc.localize(self.created_at),
                )
            )[-1]
        else:
            next_date = list(
                rrule.rrule(
                    rrule.MONTHLY,
                    interval=1,
                    until=datetime.datetime.now(datetime.UTC)
                    + relativedelta(months=+1),
                    dtstart=self.created_at,
                )
            )[-1]

        return next_date

    def showSellPrice(self) -> str:
        """Return formatted currency string of sell price
        Utility function to make jinja templating simpler.

        NOTE: Since this is the Subscription object,
        the sell_price/interval_amount comes directly from
        this model, since by this point a currency may have been
        used during the purchase of the plan.

        jinja usage:

        {{ subscription.showSellPrice() }}

        """
        if self.sell_price is None:
            result = "unknown"
        else:
            amount = self.sell_price
            result = currencyFormat(self.currency, amount)
        return result

    def showIntervalAmount(self) -> str:
        """Return formatted currency string of inverval_amount
        Utility function to make jinja templating simpler.

        NOTE: Since this is the Subscription object,
        the sell_price/interval_amount comes directly
        from this model, since by this point a currency
        may have been used during the purchase of the plan.

        jinja usage:

        {{ subscription.showIntervalAmount() }}

        """
        if self.interval_amount is None:
            result = "unknown"
        else:
            amount = self.interval_amount
            result = currencyFormat(self.currency, amount)
        return result


class SubscriptionNote(database.Model):
    __tablename__ = "subscription_note"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
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
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
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
    subscription = relationship(
        "Subscription", back_populates="upcoming_invoice"
    )  # noqa: E501


class StripeInvoice(database.Model, CreatedAt):
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
    uuid = database.Column(
        database.String(), default=uuid_string, primary_key=True
    )  # noqa: E501
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
    created = database.Column(database.Integer(), nullable=True)
    stripe_invoice_raw_json = database.Column(database.JSON(), nullable=True)


class Company(database.Model):
    __tablename__ = "company"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    name = database.Column(database.String())
    slogan = database.Column(database.String())
    logo_src = database.Column(database.String())


association_table_plan_choice_group = database.Table(
    "plan_choice_group",
    database.Column(
        "choice_group_id", database.Integer, ForeignKey("choice_group.id")
    ),  # noqa: E501
    database.Column("plan_id", database.Integer, ForeignKey("plan.id")),
)


association_table_plan_to_price_lists = database.Table(
    "plan_price_list_associations",
    database.Column(
        "plan_uuid",
        database.String,
        ForeignKey("plan.uuid"),
        primary_key=True,
    ),
    database.Column(
        "price_list_uuid",
        database.String,
        ForeignKey("price_list.uuid"),
    ),
)


# Enables: As a shop owner I can order the order in which questions are presented
# to subscribers during sign up
# See:
# https://github.com/sqlalchemy/sqlalchemy/discussions/8556#discussioncomment-3700971
class PlanQuestionAssociation(database.Model):
    __tablename__ = "plan_question_associations"
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=uuid_string)
    question_id = database.Column(database.Integer, ForeignKey("question.id"))
    question = relationship("Question")
    plan_id = database.Column(database.Integer, ForeignKey("plan.id"))
    plan = relationship("Plan")
    order = database.Column(database.Integer(), nullable=True)
    __table_args__ = (PrimaryKeyConstraint("question_id", "plan_id"),)


class INTERVAL_UNITS(Enum):
    DAILY = _("daily")
    WEEKLY = _("weekly")
    MONTHLY = _("monthly")
    YEARLY = _("yearly")


association_table_plan_to_document = database.Table(
    "plan_document_associations",
    database.Column(
        "plan_uuid",
        database.Integer,
        ForeignKey("plan.uuid"),
        primary_key=True,
    ),
    database.Column(
        "document_uuid",
        database.Integer,
        ForeignKey("document.uuid"),
    ),
)


class Plan(database.Model, HasArchived):
    __tablename__ = "plan"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    parent_plan_revision_uuid = database.Column(database.String(), default=uuid_string)
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
    # TODO associationproxy
    questions = relationship(PlanQuestionAssociation, backref="plans")
    documents = relationship("Document", secondary=association_table_plan_to_document)
    position = database.Column(database.Integer(), default=0)

    category_uuid = database.Column(
        database.Integer, ForeignKey("category.uuid")
    )  # noqa: E501
    category = relationship("Category", back_populates="plans")
    private = database.Column(database.Boolean(), default=0)
    cancel_at = database.Column(database.Integer(), default=0)
    price_lists = relationship(
        "PriceList", secondary=association_table_plan_to_price_lists
    )

    def __getattribute__(self, name):
        if name == "trial_period_days":
            """
            Ensure all shops return an int (and not None)
            for trial_period_days
            (using __getattribute__ avoids touching preexisting data on
            existing shops)
            See https://github.com/Subscribie/subscribie/issues/1315
            """
            if super(Plan, self).__getattribute__(name) is None:
                log.warning(f"trial_period_days is none for plan {self.title}")
            return super(Plan, self).__getattribute__(name) or 0
        return super(Plan, self).__getattribute__(name)

    def getPrice(self, currency):
        """Returns a tuple of sell_price and interval_amount of the plan for
        a given currency, or a tuple False, and an error message str.

        To answer the question "what is the price of this plan?" the
        questions which need answers include:

        - What currency do you want? (A plan may or may not be sold in a given currency
        - Are there any price_list rules associated with the plan + currency?
            - e.g. In the US a price rule may increase prices by x %
        - An error is returned if a price is requested for a plan with no matching
          currency, see :return:.

        :param currency: Currency code e.g. GBP
        :type currency: str
        :return: tuple sell_price, interval_amount for the plan after applying any found price_list rules, # noqa: E501
                 if no price_list is found for the desired currency, then a tuple of False, error message # noqa: E501
                 is returned.
        :rtype: tuple
        """
        # Find price_lists for plan
        log.debug(
            f"Searching for price_list in currency {currency} for plan {self.title}"  # noqa: E501
        )

        # Not all plans will have a price_list, if not, return error
        price_list_found_for_currency = False
        for price_list in self.price_lists:
            log.debug(f"only use price list if currency {currency}")

            if price_list.currency == currency:
                price_list_found_for_currency = True
                log.debug(
                    f"Found {currency} priceList: {price_list} for plan."
                )  # noqa: E501

                foundRules = []
                for rule in price_list.rules:
                    log.debug(f"Found rule: {rule}")
                    foundRules.append(rule)

                # Pass callable get_discount_code to support external context (e.g. session data) # noqa: E501
                context = {"get_discount_code": get_discount_code}
                sell_price, interval_amount = self.applyRules(
                    rules=foundRules, context=context
                )
        if price_list_found_for_currency is False:
            msg = f"Could not find price_list for currency: {currency}. There are {len(self.price_lists)} connected to this plan ({self.uuid}), but none of them are for currency {currency}"  # noqa: E501
            log.warning(msg)
            return False, msg
        log.debug(
            f"getPrice returning sell price: {sell_price} for plan {self.title}"  # noqa: E501
        )  # noqa: E501
        log.debug(
            f"getPrice returning interval_amount: {interval_amount} for plan {self.title}"  # noqa: E501
        )
        return sell_price, interval_amount

    def applyRules(self, rules=[], context={}):
        """Apply pricelist rules to a given plan

        :param rules: List of rules to apply to the plan price
        :param context: Dictionary storing session context, for example get_discount_code callable for validating discount codes # noqa: E501
        """
        log.debug(f"Applying applyRules to plan: {self.title}")

        sell_price = self.sell_price
        interval_amount = self.interval_amount
        log.debug(f"before apply_rules sell price is: {self.sell_price}")
        log.debug(
            f"before apply_rules inverval_price is: {self.interval_amount}"
        )  # noqa: E501

        def apply_percent_increase(base: int, percent_increase: int) -> int:
            add = int((base / 100) * int(percent_increase or 1))
            base += add
            return base

        def apply_percent_discount(base: int, percent_discount: int) -> int:
            minus = int((base / 100) * int(percent_discount or 1))
            base -= minus
            return base

        def apply_amount_decrease(base: int, amount_decrease: int) -> int:
            base -= int(amount_decrease or 0)
            return base

        def apply_amount_increase(base: int, amount_increase: int) -> int:
            base += int(amount_increase or 0)
            return base

        def check_discount_code_valid(
            expected_discount_code=None, f=None
        ) -> bool:  # noqa: E501
            """
            Check discount code is valid

            :param expected_discount_code: str, the expected discount code from a given rule # noqa: E501
            :param f: Callable, which must return a string of the discount code
            :return: bool success (True) or fail (False) check against rule's discount code # noqa: E501
            """
            if f is None:
                return False
            else:
                # Call the get_discount_code callable
                return expected_discount_code == f()

        def calculatePrice(
            sell_price: int, interval_amount: int, rules, context={}
        ):  # noqa: E501
            """Apply all Return tuple of sell_price, interval_amount

            :param sell_price: The base sell_price of the plan
            :type sell_price: int
            :param interval_amount: The base interval_amount
            :type interval_amount: int
            :param rules: List of rules to apply to the plan
            :type rules: list
            :param context: Context for passing callables which may access session data, like get_discount_code # noqa: E501
            :type context: dict, optional
            :return Tuple of sell_price, interval_amount after price rules have been applied, if any
            :rtype tuple
            """
            for rule in rules:
                log.debug(f"applying rule {rule}")
                if rule.requires_discount_code:
                    expected_discount_code = rule.discount_code
                    f = context["get_discount_code"]
                    if (
                        check_discount_code_valid(
                            expected_discount_code=expected_discount_code, f=f
                        )
                        is False
                    ):
                        # Skip this rule if discount_code validation fails
                        continue
                if rule.affects_sell_price and sell_price is not None:
                    if rule.percent_increase:
                        # only increase percent if the min_sell_price is higher than plan sell_price  # noqa: E501
                        if (
                            rule.has_min_sell_price
                            and sell_price >= rule.min_sell_price
                        ):
                            sell_price = apply_percent_increase(
                                sell_price, rule.percent_increase
                            )  # noqa: E501
                        else:
                            sell_price = apply_percent_increase(
                                sell_price, rule.percent_increase
                            )  # noqa: E501

                    if rule.percent_discount:
                        """
                        If I want a minimum sell price
                        Then I want a percent discount to apply if the value is
                        equal to or greater than the minimum sell price.
                        Otherwise, always apply the percent discount regardlrss
                        of sell price.
                        """
                        if (
                            rule.has_min_sell_price
                            and sell_price >= rule.min_sell_price
                        ):
                            sell_price = apply_percent_discount(
                                sell_price, rule.percent_discount
                            )  # noqa: E501
                        else:
                            sell_price = apply_percent_discount(
                                sell_price, rule.percent_discount
                            )  # noqa: E501

                    sell_price = apply_amount_decrease(
                        sell_price, rule.amount_discount
                    )  # noqa: E501

                    sell_price = apply_amount_increase(
                        sell_price, rule.amount_increase
                    )  # noqa: E501

                if (
                    rule.affects_interval_amount
                    and interval_amount is not None  # noqa: E501
                ):
                    if rule.percent_increase:
                        if (
                            rule.has_min_interval_amount
                            and rule.min_interval_amount > interval_amount
                            or rule.min_interval_amount is None
                        ):
                            interval_amount = apply_percent_increase(
                                interval_amount, rule.percent_increase
                            )  # noqa: E501

                    if rule.percent_discount:
                        if (
                            rule.min_interval_amount
                            and rule.min_interval_amount < interval_amount
                            or rule.min_interval_amount is None
                        ):
                            interval_amount = apply_percent_discount(
                                interval_amount, rule.percent_discount
                            )  # noqa: E501

                    interval_amount = apply_amount_decrease(
                        interval_amount, rule.amount_discount
                    )  # noqa: E501

                    interval_amount = apply_amount_increase(
                        interval_amount, rule.amount_increase
                    )  # noqa: E501

                log.debug(f"after apply_rules sell price is: {sell_price}")
                log.debug(
                    f"after apply_rules interval_amount is: {interval_amount}"
                )  # noqa: E501

            return sell_price, interval_amount

        sell_price, interval_amount = calculatePrice(
            sell_price, interval_amount, rules, context=context
        )  # noqa: E501

        return sell_price, interval_amount

    def getSellPrice(self, currency_code=None) -> Optional[int]:
        """Return the sell_price of a given plan after applying any price rules
        Args:
            currency_code: str of the currency requested. If currency is None,
                      then the currency is detected via geo lookup with
                      default fallback.
        Returns:
            Integer representing the sell_price after aplying any pricing riles
            or None if plan does not have a sell_price.
        """
        if currency_code is None:
            currency_code = get_geo_currency_code()
        return self.getPrice(currency_code)[0]

    def getIntervalAmount(self, currency_code=None) -> Optional[int]:
        """Return the sell_price of a given plan after applying any price rules
        Args:
            currency_code: str of the currency requested. If currency is None,
                      then the currency is detected via geo lookup with
                      default fallback.
        Returns:
            Integer representing the interval_amount after applying any pricing
            rules, or None if plan does not have an interval_amount.
        """
        log.debug(f"getIntervalAmount called with currency_code: {currency_code}")
        if currency_code is None:
            log.warning("getIntervalAmount currency_code was None")
            currency_code = get_geo_currency_code()

        return self.getPrice(currency_code)[1]

    def showSellPrice(self) -> str:
        """Return formatted currency string of sell price
        Utility function to make jinja templating simpler:

        From this:

        {{ currency_code }}{{ "%.2f"|format(plan.getSellPrice(get_geo_currency_code())/100) }} # noqa: E501

        To to this:

        {{ plan.showSellPrice() }}

        """
        currency_symbol = get_geo_currency_symbol()
        amount = self.getSellPrice(get_geo_currency_code()) / 100

        result = f"{currency_symbol}{amount:.2f}"
        return result

    def showItervalUnit(self) -> str:
        return _(INTERVAL_UNITS[self.interval_unit.upper()].value)

    def showIntervalAmount(self) -> str:
        """Return formatted currency string of interval amount
        Utility function to avoid having to be verbose in jinja
        templates: See showSellPrice

        Usage in jinja:

        {{ plan.showIntervalAmount() }}
        """
        log.debug("showIntervalAmount called")
        currency_symbol = get_geo_currency_symbol()
        log.debug(f"showIntervalAmount got currency_symbol {currency_symbol}")

        amount = self.getIntervalAmount(get_geo_currency_code()) / 100

        log.debug(
            f"showIntervalAmount amount calculated to amount: {amount}, with currency code {get_geo_currency_code()}"  # noqa: E501
        )

        result = f"{currency_symbol}{amount:.2f}"
        log.debug(f"showIntervalAmount result formatted as: {result}")
        return result

    def assignDefaultPriceLists(self):
        existing_price_list = PriceList.query.all()
        for price_list in existing_price_list:
            log.debug(f"Added price_list {price_list.name} to {self.title}")
            self.price_lists.append(price_list)
            log.debug(f"Added price_list {price_list.name} to {self.title}")
        return self.price_lists

    def is_free(self):
        """
        Return True if plan requirements mean plan is free
        Return False if plan requirements mean plan is not free

        Note this method does NOT take pricelists into account.

        #TODO take pricelists into account (because a product may *become*
        free, based on a date rule for example).
        """
        if (
            self.requirements.instant_payment is False
            and self.requirements.subscription is False
        ):
            return True
        return False


class Category(database.Model):
    __tablename__ = "category"
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=uuid_string)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    name = database.Column(database.String())
    plans = relationship("Plan", back_populates="category")
    position = database.Column(database.Integer(), default=0)


class PlanRequirements(database.Model):
    __tablename__ = "plan_requirements"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    plan_id = database.Column(database.Integer(), ForeignKey("plan.id"))
    plan = relationship("Plan", back_populates="requirements")
    instant_payment = database.Column(database.Boolean(), default=False)
    subscription = database.Column(database.Boolean(), default=False)
    note_to_seller_required = database.Column(database.Boolean(), default=False)  # noqa
    note_to_buyer_message = database.Column(database.String())


class PlanSellingPoints(database.Model):
    __tablename__ = "plan_selling_points"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    point = database.Column(database.String())
    plan_id = database.Column(database.Integer(), ForeignKey("plan.id"))
    plan = relationship("Plan", back_populates="selling_points")


class Integration(database.Model):
    __tablename__ = "integration"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    google_tag_manager_active = database.Column(database.Boolean())
    google_tag_manager_container_id = database.Column(database.String())
    tawk_active = database.Column(database.Boolean())
    tawk_property_id = database.Column(database.String())


# stripe_active:
# True(1) if the subscriber has connected to stripe either in test mode or live mode
# False(0) if the subscriber has not yet connected to stripe
# stripe_livemode:
# True(1) if stripe is in live mode
# False(0) if stripe is in test mode


class PaymentProvider(database.Model):
    __tablename__ = "payment_provider"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    gocardless_active = database.Column(database.Boolean())
    gocardless_access_token = database.Column(database.String())
    gocardless_environment = database.Column(database.String())
    stripe_active = database.Column(database.Boolean(), default=False)
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
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    page_name = database.Column(database.String())
    path = database.Column(database.String())
    template_file = database.Column(database.String())
    private = database.Column(database.Boolean(), default=0)


class Module(database.Model):
    __tablename__ = "module"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    name = database.Column(database.String())
    src = database.Column(database.String())


class Transaction(database.Model):
    __tablename__ = "transactions"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    currency = database.Column(database.String(), nullable=False)
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
    is_donation = database.Column(database.Boolean(), default=0)

    def showSellPrice(self) -> str:
        currency_symbol = get_geo_currency_symbol()
        amount = self.amount / 100
        result = f"{currency_symbol}{amount:.2f}"
        return result


class SeoPageTitle(database.Model):
    __tablename__ = "module_seo_page_title"
    path = database.Column(database.String(), primary_key=True)
    title = database.Column(database.String())


class ChoiceGroup(database.Model):
    __tablename__ = "choice_group"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    title = database.Column(database.String())
    options = relationship("Option", back_populates="choice_group")


class Question(database.Model):
    __tablename__ = "question"
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=uuid_string)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    options = relationship("QuestionOption", back_populates="question")
    title = database.Column(database.String())


class QuestionOption(database.Model):
    __tablename__ = "question_option"
    id = database.Column(database.Integer(), primary_key=True)
    question_id = database.Column(database.Integer(), ForeignKey("question.id"))  # noqa
    question = relationship("Question", back_populates="options")
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    title = database.Column(database.String())
    description = database.Column(database.Text())
    primary_icon = database.Column(database.String())


class Answer(database.Model):
    __tablename__ = "answer"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    question_id = database.Column(database.Integer())
    question_title = database.Column(database.String())
    response = database.Column(database.String())
    subscription_id = database.Column(
        database.Integer(), ForeignKey("subscription.id")
    )  # noqa
    subscription = relationship(
        "Subscription", back_populates="question_answers"
    )  # noqa


class Option(database.Model):
    __tablename__ = "option"
    id = database.Column(database.Integer(), primary_key=True)
    choice_group_id = database.Column(
        database.Integer(), ForeignKey("choice_group.id")
    )  # noqa
    choice_group = relationship("ChoiceGroup", back_populates="options")
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    title = database.Column(database.String())
    description = database.Column(database.Text())
    primary_icon = database.Column(database.String())


class ChosenOption(database.Model):
    __tablename__ = "chosen_option"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
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
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
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
    default_currency = database.Column(database.String(), default=None)
    default_country_code = database.Column(database.String(), default=None)
    shop_activated = database.Column(database.Boolean(), default=False)
    api_key_secret_live = database.Column(database.String(), default=None)
    api_key_secret_test = database.Column(database.String(), default=None)
    donations_enabled = database.Column(database.Boolean(), default=False)
    custom_thank_you_url = database.Column(database.String(), default=None)


class File(database.Model):
    """File uploads meta"""

    __tablename__ = "file"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    file_name = database.Column(database.String())


class Document(database.Model, HasArchived, HasReadOnly):
    """Raw text Document"""

    __tablename__ = "document"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    name = database.Column(database.String(), default=None)
    type = database.Column(database.String(), default=None)
    body = database.Column(database.String(), default=None)
    plans = relationship(
        "Plan",
        secondary=association_table_plan_to_document,
        back_populates="documents",
    )
    subscriptions = relationship(
        "Subscription",
        secondary=association_table_subscription_to_document,
        back_populates="documents",
    )


class TaxRate(database.Model):
    """Stripe Tax Rate ids"""

    __tablename__ = "tax_rate"
    id = database.Column(database.Integer(), primary_key=True)
    stripe_tax_rate_id = database.Column(database.String())
    stripe_livemode = database.Column(database.Boolean())
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )


association_table_price_list_to_rule = database.Table(
    "price_list_rules_associations",
    database.Column(
        "price_list_uuid",
        database.Integer,
        ForeignKey("price_list.uuid"),
        primary_key=True,
    ),
    database.Column(
        "price_list_rule_uuid",
        database.Integer,
        ForeignKey("price_list_rule.uuid"),
    ),
)


class PriceList(database.Model):
    """
    PriceList table

    Purpose: Stores a price list for each currency (note this is per currency,
    not per plan).
    e.g. As a shop owner, I can create a USD price list which increases all
    prices by 10% of the base price, by assigning PriceListRules to a PriceList

    Usage example:
    >>> from subscribie.database import database
    >>> from subscribie.models import PriceListRule, PriceList
    >>> priceList = PriceList(name="Christmas USD", currency="USD")
    >>> rule = PriceListRule(percent_discount=25, name="25% Discount")
    >>> priceList.rules.append(rule)
    >>> database.session.add(priceList)
    >>> database.session.commit()
    >>> PriceList.query.all()
    [<PriceList 1>]
    >>> PriceList.query.all()[0].__dict__
    {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x7f60e0a3b820>, 'id': 2, 'uuid': '1aad2818-42ab-4493-b5f2-1fa64497a784', 'start_date': datetime.datetime(2022, 6, 19, 20, 39, 44, 180493), 'currency': 'USD', 'created_at': datetime.datetime(2022, 6, 19, 20, 39, 44, 180368), 'name': 'Christmas USD', 'expire_date': None} # noqa: E501
    >>> price_list = PriceList.query.first()
    >>> plan = Plan.query.first()
    >>> plan.price_lists.append(price_list)
    >>> database.session.add(plan)
    >>> database.session.commit()

    """

    __tablename__ = "price_list"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    name = database.Column(database.String())
    start_date = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    expire_date = database.Column(database.DateTime, default=None)
    currency = database.Column(database.String())
    rules = relationship(
        "PriceListRule", secondary=association_table_price_list_to_rule
    )
    plans = relationship(
        "Plan",
        secondary=association_table_plan_to_price_lists,
        back_populates="price_lists",
    )


class PriceListRule(database.Model):
    """
    PriceListRule table

    Each plan can have a related active price list per currency, but (never?)
    more than one active price list per currency.

    e.g. As a shop owner selling in GBP by default, I want to sell plan A in
    USD and GBP.
    There will be at most 2 PriceList(s), one for GBP and one for USD.

    Note: There may be a PriceList per currency, a PriceList per plan is
          NOT required or recommended as there would be to mant PriceLists
          to manage. Instead, use PriceListRule(s) and assign rule(s) to
          PriceList(s)

    At least, there would be 1 PriceList: One for USD, a second PriceList is
    not mandatory for GBP since that is the default currency. However, the
    moment the shop owner wants to apply special price rules for GBP, the
    shop owner would need to create a GBP PriceList
    (e.g. a single GBP PriceList with two PriceListRule(s)
    giving 10% off, for subscriptions over £50
    """

    __tablename__ = "price_list_rule"
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    uuid = database.Column(database.String(), default=uuid_string)
    name = database.Column(database.String())
    start_date = database.Column(
        database.DateTime, default=datetime.datetime.now(datetime.UTC)
    )
    expire_date = database.Column(database.DateTime, default=None)
    active = database.Column(database.Boolean(), default=1)
    position = database.Column(database.Integer(), default=0)
    affects_sell_price = database.Column(database.Boolean(), default=1)
    affects_interval_amount = database.Column(database.Boolean(), default=1)
    percent_discount = database.Column(database.Integer(), default=0)
    percent_increase = database.Column(database.Integer(), default=0)
    amount_discount = database.Column(database.Integer(), default=0)
    amount_increase = database.Column(database.Integer(), default=0)
    min_sell_price = database.Column(database.Integer(), default=None)
    has_min_sell_price = database.Column(database.Boolean(), default=False)
    min_interval_amount = database.Column(database.Integer(), default=None)
    has_min_interval_amount = database.Column(database.Boolean(), default=False)
    requires_discount_code = database.Column(database.Boolean(), default=0)
    price_lists = relationship(
        "PriceList",
        secondary=association_table_price_list_to_rule,
        back_populates="rules",
    )
