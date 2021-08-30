import logging
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
    jsonify,
    current_app,
)
from subscribie.models import (
    Plan,
    Option,
    ChosenOption,
    Person,
    PaymentProvider,
    Company,
    Subscription,
    Transaction,
    SubscriptionNote,
    Setting,
    TaxRate,
)
from subscribie.utils import (
    get_stripe_publishable_key,
    get_stripe_secret_key,
    format_to_stripe_interval,
    create_stripe_tax_rate,
    get_stripe_livemode,
    get_stripe_connect_account_id,
)
from subscribie.forms import CustomerForm
from subscribie.database import database
from subscribie.signals import journey_complete
from subscribie.email import send_welcome_email
from subscribie.notifications import newSubscriberEmailNotification
import stripe
import backoff
import os
import json
from uuid import uuid4
import sqlalchemy

log = logging.getLogger(__name__)
checkout = Blueprint("checkout", __name__, template_folder="templates")


@checkout.route("/new_customer", methods=["GET"])
def new_customer():
    plan = Plan.query.filter_by(uuid=request.args["plan"]).first()
    if plan is None:
        log.warning(
            f'Plan {request.args["plan"]} requested at /new_customer route but not found'  # noqa
        )
        return redirect(url_for("index"))
    session["plan"] = plan.uuid

    # Fetch selected options, if present
    chosen_options = []
    if session.get("chosen_option_ids", None):
        for option_id in session["chosen_option_ids"]:
            option = Option.query.get(option_id)
            if option is not None:
                # We will store as ChosenOption because option may change after the order # noqa
                # has processed. This preserves integrity of the actual chosen options
                chosen_option = ChosenOption()
                chosen_option.option_title = option.title
                chosen_option.choice_group_title = option.choice_group.title
                chosen_options.append(chosen_option)
            else:
                log.error(f"Failed to get Open from session option_id: {option_id}")

    package = request.args.get("plan", "not set")
    session["package"] = package
    plan = Plan.query.filter_by(uuid=request.args.get("plan")).first()
    form = CustomerForm()
    return render_template(
        "new_customer.html",
        form=form,
        package=package,
        plan=plan,
        chosen_options=chosen_options,
    )


@checkout.route("/new_customer", methods=["POST"])
def store_customer():
    form = CustomerForm()
    if form.validate():
        given_name = form.data["given_name"]
        family_name = form.data["family_name"]
        address_line_one = form.data["address_line_one"]
        city = form.data["city"]
        postcode = form.data["postcode"]
        email = form.data["email"]
        mobile = form.data["mobile"]
        # Store customer in session
        sid = session["sid"]
        # Store email in session
        session["email"] = email
        session["given_name"] = given_name

        # Store person info in session for form pre-population
        session["given_name"] = given_name
        session["family_name"] = family_name
        session["address_line_one"] = address_line_one
        session["city"] = city
        session["postcode"] = postcode
        session["email"] = email
        session["mobile"] = mobile

        # Don't store person if already exists
        try:
            person = Person.query.filter_by(email=email).one()
        except sqlalchemy.orm.exc.NoResultFound:
            person = None
        except sqlalchemy.orm.exc.MultipleResultsFound:
            person = Person.query.filter_by(email=email).all()[0]

        if person is None:
            # Store person, with randomly generated password
            person = Person(
                sid=sid,
                given_name=given_name,
                family_name=family_name,
                address_line1=address_line_one,
                city=city,
                postal_code=postcode,
                email=email,
                mobile=mobile,
                password=str(os.urandom(16)),
                password_expired=1,
            )
            database.session.add(person)
            database.session.commit()
        session["person_id"] = person.id
        # Store note to seller in session if there is one
        note_to_seller = form.data["note_to_seller"]
        session["note_to_seller"] = note_to_seller

        return redirect(url_for("checkout.order_summary"))
    else:
        return "There was an error processing that form, please go back and try again."


@checkout.route("/order-summary", methods=["GET"])
def order_summary():
    payment_provider = PaymentProvider.query.first()
    if (
        payment_provider.stripe_livemode
        and payment_provider.stripe_live_connect_account_id is None
        or payment_provider.stripe_livemode is False
        and payment_provider.stripe_test_connect_account_id is None
    ):

        return """Shop owner has not connected Stripe payments yet.
                This can be done by the shop owner via the admin dashboard."""

    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    stripe_pub_key = get_stripe_publishable_key()
    company = Company.query.first()
    stripe_create_checkout_session_url = url_for(
        "checkout.stripe_create_checkout_session"
    )

    if payment_provider.stripe_livemode:
        stripe_connected_account_id = payment_provider.stripe_live_connect_account_id
    else:
        stripe_connected_account_id = payment_provider.stripe_test_connect_account_id

    return render_template(
        "order_summary.html",
        company=company,
        plan=plan,
        fname=session["given_name"],
        stripe_pub_key=stripe_pub_key,
        stripe_create_checkout_session_url=stripe_create_checkout_session_url,
        stripe_connected_account_id=stripe_connected_account_id,
    )


@checkout.route("/instant_payment_complete", methods=["GET"])
def instant_payment_complete():
    scheme = "https" if request.is_secure else "http"
    return redirect(url_for("checkout.thankyou", _scheme=scheme, _external=True))


@checkout.route("/thankyou", methods=["GET"])
def thankyou():
    if session.get("plan") is None:
        log.warn("Visit to /thankyou with no plan in session")
        return redirect("/")
    # Remove subscribie_checkout_session_id from session
    checkout_session_id = session.pop("subscribie_checkout_session_id", None)
    subscription = (
        database.session.query(Subscription)
        .filter_by(subscribie_checkout_session_id=checkout_session_id)
        .first()
    )

    # Store note to seller if in session
    if session.get("note_to_seller", False) is not False and subscription is not None:
        note = SubscriptionNote(
            note=session["note_to_seller"], subscription_id=subscription.id
        )
        database.session.add(note)

    database.session.commit()

    # Send journey_complete signal
    email = session.get("email", current_app.config["MAIL_DEFAULT_SENDER"])
    journey_complete.send(current_app._get_current_object(), email=email)

    send_welcome_email()

    return render_template("thankyou.html")


@checkout.route("/stripe-create-checkout-session", methods=["POST"])
def stripe_create_checkout_session():
    data = request.json

    # If VAT tax is enabled, get stripe tax id
    settings = Setting.query.first()
    if settings is not None:
        charge_vat = settings.charge_vat
        create_stripe_tax_rate()
        tax_rate = TaxRate.query.filter_by(
            stripe_livemode=get_stripe_livemode()
        ).first()
    else:
        charge_vat = False

    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    person = Person.query.get(session["person_id"])
    charge = {}
    charge["sell_price"] = plan.sell_price
    charge["interval_amount"] = plan.interval_amount
    charge["currency"] = "GBP"
    session["subscribie_checkout_session_id"] = str(uuid4())
    payment_method_types = ["card"]
    success_url = url_for(
        "checkout.instant_payment_complete", _external=True, plan=plan.uuid
    )
    cancel_url = url_for("checkout.order_summary", _external=True)

    stripe.api_key = get_stripe_secret_key()

    metadata = {
        "person_uuid": person.uuid,
        "plan_uuid": session["plan"],
        "chosen_option_ids": json.dumps(session.get("chosen_option_ids", None)),
        "package": session.get("package", None),
        "subscribie_checkout_session_id": session.get(
            "subscribie_checkout_session_id", None
        ),
    }

    # Add note to seller if present directly on payment metadata
    if session.get("note_to_seller", False):
        metadata["note_to_seller"] = session.get("note_to_seller")

    if plan.requirements.subscription:
        subscription_data = {
            "application_fee_percent": 1.25,
            "metadata": {
                "person_uuid": person.uuid,
                "plan_uuid": session["plan"],
                "chosen_option_ids": json.dumps(
                    session.get("chosen_option_ids", None)
                ),  # noqa
                "package": session.get("package", None),
                "subscribie_checkout_session_id": session.get(
                    "subscribie_checkout_session_id", None
                ),
            },
        }
        if plan.trial_period_days > 0:
            subscription_data["trial_period_days"] = plan.trial_period_days

        if charge_vat:
            subscription_data["default_tax_rates"] = [tax_rate.stripe_tax_rate_id]
        # Add note to seller if present on subscription_data metadata
        if session.get("note_to_seller", False):
            subscription_data["metadata"]["note_to_seller"] = session.get(
                "note_to_seller"
            )
        # Add trial period if present
        if plan.days_before_first_charge and plan.days_before_first_charge > 0:
            subscription_data["trial_period_days"] = plan.days_before_first_charge

    if plan.requirements.instant_payment:
        payment_intent_data = {"application_fee_amount": 20, "metadata": metadata}

    if plan.requirements.subscription:
        mode = "subscription"
    else:
        mode = "payment"

    # Build line_items array depending on plan requirements
    line_items = []

    # Add line item for instant_payment if required
    if plan.requirements.instant_payment:
        # Append "Up-front fee" to product name if also a subscription
        plan_name = plan.title
        if plan.requirements.subscription:
            plan_name = "(Up-front fee) " + plan_name

        tax_rates = [tax_rate.stripe_tax_rate_id] if charge_vat is True else []
        line_items.append(
            {
                "tax_rates": tax_rates,
                "price_data": {
                    "currency": charge["currency"],
                    "product_data": {
                        "name": plan_name,
                    },
                    "unit_amount": charge["sell_price"],
                },
                "quantity": 1,
            }
        )

    if plan.requirements.subscription:
        line_items.append(
            {
                "price_data": {
                    "recurring": {
                        "interval": format_to_stripe_interval(plan.interval_unit)
                    },
                    "currency": charge["currency"],
                    "product_data": {
                        "name": plan.title,
                    },
                    "unit_amount": charge["interval_amount"],
                },
                "quantity": 1,
            }
        )

    # Create Stripe checkout session for payment or subscription mode
    if plan.requirements.subscription:
        stripe_session = stripe.checkout.Session.create(
            stripe_account=data["account_id"],
            payment_method_types=payment_method_types,
            line_items=line_items,
            mode=mode,
            metadata=metadata,
            customer_email=person.email,
            success_url=success_url,
            cancel_url=cancel_url,
            subscription_data=subscription_data,
        )
        return jsonify(id=stripe_session.id)
    elif plan.requirements.instant_payment:
        stripe_session = stripe.checkout.Session.create(
            stripe_account=data["account_id"],
            payment_method_types=payment_method_types,
            line_items=line_items,
            mode=mode,
            metadata=metadata,
            customer_email=person.email,
            success_url=success_url,
            cancel_url=cancel_url,
            payment_intent_data=payment_intent_data,
        )
        return jsonify(id=stripe_session.id)


def create_subscription(
    email=None,
    package=None,
    chosen_option_ids=None,
    subscribie_checkout_session_id=None,
    stripe_external_id=None,
    stripe_subscription_id=None,
) -> Subscription:
    """Create subscription model
    Note: A subscription model is also created if a plan only has
    one up_front payment (no recuring subscription). This allows
    the storing of chosen options againt their plan choice.
    Chosen option ids may be passed via webhook or through session
    """
    log.info("Creating Subscription model if needed")
    subscription = None  # Initalize subscription model to None

    # Store Subscription against Person locally
    if email is None:
        email = session["email"]

    if package is None:
        package = session["package"]

    person = database.session.query(Person).filter_by(email=email).one()

    # subscribie_checkout_session_id can be passed by stripe metadata (webhook) or
    # via session (e.g. when session only with no up-front payment)
    if subscribie_checkout_session_id is None:
        subscribie_checkout_session_id = session.get(
            "subscribie_checkout_session_id", None
        )
    log.info(f"subscribie_checkout_session_id is: {subscribie_checkout_session_id}")

    # Verify Subscription not already created (e.g. stripe payment webhook)
    # another hook or mandate only payment may have already created the Subscription
    # model, if so, fetch it via its subscribie_checkout_session_id
    if subscribie_checkout_session_id is not None:
        subscription = (
            Subscription.query.filter_by(
                subscribie_checkout_session_id=subscribie_checkout_session_id
            )
            .filter(Subscription.person.has(email=email))
            .first()
        )

    if subscription is None:
        log.info("No existing subscription model found, creating Subscription model")
        # Create new subscription model
        subscription = Subscription(
            sku_uuid=package,
            person=person,
            subscribie_checkout_session_id=subscribie_checkout_session_id,
            stripe_external_id=stripe_external_id,
            stripe_subscription_id=stripe_subscription_id,
        )
        # Add chosen options (if any)
        if chosen_option_ids is None:
            chosen_option_ids = session.get("chosen_option_ids", None)

        if chosen_option_ids:
            log.info(f"Applying chosen_option_ids to subscription: {chosen_option_ids}")
            chosen_options = []
            for option_id in chosen_option_ids:
                log.info(f"Locating option id: {option_id}")
                option = Option.query.get(option_id)
                # Store as ChosenOption because options may change after the order
                # has processed. This preserves integrity of the actual chosen options
                chosen_option = ChosenOption()
                if option is not None:
                    chosen_option.option_title = option.title
                    chosen_option.choice_group_title = option.choice_group.title
                    chosen_option.choice_group_id = (
                        option.choice_group.id
                    )  # Used for grouping latest choice
                    chosen_options.append(chosen_option)
                else:
                    log.error(f"Failed to get Open from session option_id: {option_id}")
            subscription.chosen_options = chosen_options
        else:
            log.info("No chosen_option_ids were found or applied.")

        database.session.add(subscription)
        database.session.commit()
        session["subscription_uuid"] = subscription.uuid

        # If subscription plan has cancel_at set, modify Stripe subscription
        # charge_at property
        stripe.api_key = get_stripe_secret_key()
        connect_account_id = get_stripe_connect_account_id()
        if subscription.plan.cancel_at:
            cancel_at = subscription.plan.cancel_at
            try:
                stripe.Subscription.modify(
                    sid=subscription.stripe_subscription_id,
                    stripe_account=connect_account_id,
                    cancel_at=cancel_at,
                )
                subscription.stripe_cancel_at = cancel_at
                database.session.commit()
            except Exception as e:  # noqa
                log.error("Could not set cancel_at: {e}")

    newSubscriberEmailNotification()
    return subscription


@backoff.on_exception(backoff.expo, Exception, max_tries=20)
def stripe_process_event_payment_intent_succeeded(event):
    """Store suceeded payment_intents as transactions
    These events will fire both at the begining of a subscription,
    and also at each successful recuring billing cycle.

    We use backoff because webhook event order is not guaranteed
    """
    log.info("Processing payment_intent.succeeded")

    data = event["data"]["object"]
    stripe.api_key = get_stripe_secret_key()
    subscribie_subscription = None

    # Get the Subscribie subscription id from Stripe subscription metadata
    try:
        subscribie_checkout_session_id = data["metadata"][
            "subscribie_checkout_session_id"
        ]
    except KeyError:
        # There is no metadata on the event if its an upfront payment
        # So try and get it via the data['invoice'] attribute
        invoice_id = data["invoice"]
        invoice = stripe.Invoice.retrieve(
            stripe_account=event["account"], id=invoice_id
        )
        # Fetch subscription via its invoice
        subscription = stripe.Subscription.retrieve(
            stripe_account=event["account"], id=invoice.subscription
        )
        subscribie_checkout_session_id = subscription.metadata[
            "subscribie_checkout_session_id"
        ]
    except Exception as e:
        msg = f"Unable to get subscribie_checkout_session_id from event\n{e}"
        log.error(msg)
        return msg, 500

    # Locate the Subscribie subscription by its subscribie_checkout_session_id
    subscribie_subscription = (
        database.session.query(Subscription)
        .filter_by(subscribie_checkout_session_id=subscribie_checkout_session_id)
        .first()
    )

    # Store the transaction in Transaction model
    # (regardless of if subscription or just one-off plan)
    if (
        database.session.query(Transaction).filter_by(external_id=data["id"]).first()
        is None
    ):
        transaction = Transaction()
        transaction.amount = data["amount"]
        transaction.payment_status = (
            "paid" if data["status"] == "succeeded" else data["status"]
        )
        transaction.external_id = data["id"]
        transaction.external_src = "stripe"
        if subscribie_subscription is not None:
            transaction.person = subscribie_subscription.person
            transaction.subscription = subscribie_subscription
        elif data["metadata"] == {}:
            log.warn(f"Empty metadata: {data}")
            return "Empty metadata", 422
        else:
            log.error(
                "subscribie_subscription not found for this\
              payment_intent.succeeded. The metadata was:"
            )
            log.error(data["metadata"])
            raise Exception
        database.session.add(transaction)
        database.session.commit()
    return "OK", 200


@checkout.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    """Recieve stripe webhook from proxy (not directly from Stripe)

    All stripe connect webhooks are routed from a single endpoint which
    send the webhook event to the correct shop, based on the
    stripe connect account id sent in the event.

    See https://github.com/Subscribie/subscribie/issues/352
    """
    event = request.json

    log.info(f"Received stripe webhook event type {event['type']}")

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        log.info("Processing checkout.session.completed event")
        session = event["data"]["object"]
        try:
            subscribie_checkout_session_id = session["metadata"][
                "subscribie_checkout_session_id"
            ]
        except KeyError as e:
            subscribie_checkout_session_id = None
            log.warning(
                f"Could not get subscribie_checkout_session_id from session metadata in webhook checkout.session.completed: {e}"  # noqa: E501
            )
            log.warning(f"The provided metadata (if any) was: {session['metadata']}")

        if session["mode"] == "subscription":
            stripe_subscription_id = session["subscription"]
        else:
            stripe_subscription_id = None

        try:
            chosen_option_ids = session["metadata"]["chosen_option_ids"]
            chosen_option_ids = json.loads(chosen_option_ids)
        except KeyError:
            chosen_option_ids = None
        try:
            package = session["metadata"]["package"]
        except KeyError:
            package = None

        """
        We treat Stripe checkout session.mode equally because
        a subscribie plan may either be a one-off plan or a
        recuring plan. A 'subscription' is still created in the
        subscribie database regardless of if the Stripe session
        mode is "payment" or "subscription".
        See https://stripe.com/docs/api/checkout/sessions/object
        """
        if session["mode"] == "subscription" or session["mode"] == "payment":
            create_subscription(
                email=session["customer_email"],
                package=package,
                chosen_option_ids=chosen_option_ids,
                subscribie_checkout_session_id=subscribie_checkout_session_id,
                stripe_subscription_id=stripe_subscription_id,
                stripe_external_id=session["id"],
            )
        return "OK", 200

    if event["type"] == "payment_intent.succeeded":
        return stripe_process_event_payment_intent_succeeded(event)

    if event["type"] == "payment_intent.payment_failed":
        intent = event["data"]["object"]
        error_message = (
            intent["last_payment_error"]["message"]
            if intent.get("last_payment_error")
            else None
        )
        log.warning(f"Payment intent failed: {intent['id']}, {error_message}")
        # TODO Notify the customer that payment failed
        return "OK", 200

    msg = {"msg": "Unknown event", "event": event}
    log.debug(msg)

    return jsonify(msg), 422
