import logging
import requests
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
    User,
    Plan,
    Option,
    ChosenOption,
    Question,
    Answer,
    Person,
    PaymentProvider,
    Company,
    Subscription,
    Transaction,
    SubscriptionNote,
    Setting,
    TaxRate,
    SpamEmailDomain,
)
from subscribie.email import EmailMessageQueue
from subscribie.utils import (
    get_stripe_publishable_key,
    get_stripe_secret_key,
    format_to_stripe_interval,
    create_stripe_tax_rate,
    get_stripe_livemode,
    get_stripe_connect_account_id,
    get_geo_currency_code,
    get_stripe_invoices,
)
from subscribie.forms import CustomerForm, DonationForm
from subscribie.database import database
from subscribie.signals import (
    signal_journey_complete,
    signal_new_subscriber,
    signal_payment_failed,
    signal_new_donation,
)
import stripe
import backoff
import os
import json
from uuid import uuid4
import sqlalchemy
from sqlalchemy import desc

log = logging.getLogger(__name__)
checkout = Blueprint("checkout", __name__, template_folder="templates")


@checkout.route("/donate", methods=["GET"])
def donate_form():
    form = CustomerForm()
    return render_template("donation_form.html", form=form)


@checkout.route("/new_customer", methods=["GET"])
def new_customer():
    # Verify that shop owner email address is not
    # a suspected SUSPECTED_SPAM_EMAIL_DOMAINS
    user = User.query.first()
    SUSPECTED_SPAM_EMAIL_DOMAINS = [d.domain for d in SpamEmailDomain.query.all()]
    user_email_domain = user.email.split("@")[1]
    if user_email_domain in SUSPECTED_SPAM_EMAIL_DOMAINS:
        log.error(f"SUSPECTED_SPAM_EMAIL_DOMAIN {user.email} " "attempted to sign up")
        return "<h1>Please contact support before signing-up, thank you.</h1>"

    session["subscribie_checkout_session_id"] = str(uuid4())
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
@checkout.route("/new_donation", methods=["POST"])
def store_customer():
    """
    Store person information for either a plan or donation
    - Note that this endpoint services both `/new_customer` & `/new_donation'
      because the data captured at this stage is the same regardless of reason
      for payment.
    - Person data is common regardless of if the checkout flow is for
       a donation or a subscription
      (a person with an address) so we avoid duplicating that.
    """
    form = CustomerForm()
    if form.validate():
        # Check if this checkout flow is a donation
        session["is_donation"] = False
        if "new_donation" in request.path:
            session["is_donation"] = True
            form = DonationForm()
            if form.validate() is False:
                log.error(f"Error validating donation form. {form.errors}")
                return "Please try again later. We have logged the error."
            session["donation_amount"] = form.donation_amount.data
            session["donation_comment"] = form.data["note_to_seller"]

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
                email=email.lower(),
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
    plan = None
    payment_provider = PaymentProvider.query.first()
    chosen_option_ids = session.get("chosen_option_ids", None)
    # Check if checkout flow is a donation
    is_donation = session.get("is_donation", False)

    # We create a subscription object regardless of payment
    # See https://github.com/Subscribie/subscribie/issues/1369
    # note this occurs *before* directing the user to checkouts
    # (such as Stripe) since payment is separate from the
    # *intent* to create a subscription (that is, a subscription may
    # be created, with a failure to pay in a business context, and
    # such subscription would be in arrears (so long as the subscription
    # plan is not free).
    # Marking a subscription as having a checkout flow attached to it
    # is a therefore a separate asynchronous event which may or may not happen
    # right after a subscription creation, at which point, the created subscription
    # must be updated with checkout session attributes such as
    # `stripe_subscription_id=stripe_subscription_id` and `stripe_external_id`
    # The existence of a subscription object may be located by its
    # `subscribie_checkout_session_id` (an identifier created by subscribie, not
    # an external payment provider such as Stripe)
    subscribie_checkout_session_id = session.get("subscribie_checkout_session_id")
    log.info(
        f"Calling create_subscription with subscribie_checkout_session_id: {subscribie_checkout_session_id}"  # noqa: E501
    )
    if is_donation is False:
        create_subscription(
            email=session["email"],
            package=session.get("package", None),
            currency=get_geo_currency_code(),
            chosen_option_ids=chosen_option_ids,
            chosen_question_ids_answers=session.get("chosen_question_ids_answers"),
            subscribie_checkout_session_id=subscribie_checkout_session_id,  # noqa: E501
        )

    # If is a donation, then there is no plan associated
    if is_donation is False:
        plan = (
            Plan.query.execution_options(include_archived=True)
            .filter_by(uuid=session["plan"])
            .first()
        )
        if plan.archived:
            log.warning(
                "Person is signing up to an archived plan. "
                "This can happen if a checkout session has started, "
                "but not ended, and a shop owner makes an edit to a given plan"
            )
        # if plan is free, skip Stripe checkout and store subscription right away
        if plan.is_free():
            log.info("Plan is free, so skipping Stripe checkout")

            return redirect(url_for("checkout.thankyou"))

    # Since we're about to attempt a payment, verify Stripe is connected
    # before proceeding.
    if (
        payment_provider.stripe_livemode
        and payment_provider.stripe_live_connect_account_id is None
        or payment_provider.stripe_livemode is False
        and payment_provider.stripe_test_connect_account_id is None
    ):
        return """Shop owner has not connected Stripe payments yet.
                    This can be done by the shop owner via the admin dashboard."""

    # Get Stripe keys
    stripe_pub_key = get_stripe_publishable_key()
    stripe_create_checkout_session_url = url_for(
        "checkout.stripe_create_checkout_session"
    )

    if payment_provider.stripe_livemode:
        stripe_connected_account_id = payment_provider.stripe_live_connect_account_id
    else:
        stripe_connected_account_id = payment_provider.stripe_test_connect_account_id

    if is_donation is False:
        return render_template(
            "order_summary.html",
            plan=plan,
            fname=session["given_name"],
            stripe_pub_key=stripe_pub_key,
            stripe_create_checkout_session_url=stripe_create_checkout_session_url,
            stripe_connected_account_id=stripe_connected_account_id,
        )
    elif is_donation is True:
        return render_template(
            "donation_summary.html",
            fname=session["given_name"],
            stripe_pub_key=stripe_pub_key,
            stripe_create_checkout_session_url=stripe_create_checkout_session_url,
            stripe_connected_account_id=stripe_connected_account_id,
        )


@checkout.route("/instant_payment_complete", methods=["GET"])
def instant_payment_complete():
    scheme = "https" if request.is_secure else "http"
    return redirect(url_for("checkout.thankyou", _scheme=scheme, _external=True))


def return_thankyou_page():
    settings = Setting.query.first()
    # If a custom_thank_you_url is set,
    # get custom_thank_you_url
    # so can redirect subscriber to the custom_thank_you_url
    # otherwise use default thankyou.html
    # https://github.com/Subscribie/subscribie/issues/1219
    custom_thank_you_url = settings.custom_thank_you_url
    if custom_thank_you_url is None:
        return render_template("thankyou.html")
    else:
        return redirect(custom_thank_you_url)


@checkout.route("/thankyou", methods=["GET"])
def thankyou():
    is_donation = session.get("is_donation", False)

    # Prevent direct visits to /thankyou with invalid sessions
    if session.get("plan") is None and is_donation is False:
        log.warn("Visit to /thankyou with no plan in session")
        return redirect("/")

    # Remove subscribie_checkout_session_id from session
    checkout_session_id = session.pop("subscribie_checkout_session_id", None)
    if checkout_session_id is None:
        log.warning(
            """checkout_session_id returned None. redirecting to thank you page.\n
            This can happen if the thank you page is reloaded, for example."""
        )
        return return_thankyou_page()

    # Activate shop if session["sitename"] present
    if session.get("sitename"):
        # Build activation api request
        sitename = session.get("sitename")
        SAAS_API_KEY = current_app.config.get("SAAS_API_KEY")
        if "127.0.0.1" in request.remote_addr and not request.is_secure:
            scheme = "http"  # allow local development
        else:
            scheme = "https"
        activate_shop_url = (
            f"{scheme}://{sitename}/api/v1/activate-shop?SAAS_API_KEY={SAAS_API_KEY}"
        )
        # Activate the shop by calling the activate shop api request
        try:
            req = requests.get(activate_shop_url, timeout=1)
            log.info(f"Activating shop {sitename}")
            if req.status_code == 200:
                log.info(f"Succeed activating shop. status_code: {req.status_code}")
            # Set site url for login button on thank you page
            session["site-url"] = f"{scheme}://{sitename}"
            # Remove sitename from session as no longer needed
            session.pop("sitename")
        except requests.exceptions.ConnectionError as e:
            log.error(
                f"Unable to activate shop {sitename}. Could not make api request to activate: {e}."  # noqa: E501
            )  # noqa: E501
        except requests.HTTPError as e:
            log.error(
                f"Unable to activate shop {sitename}. HTTPError: {e}."
            )  # noqa: E501
        except Exception as e:
            log.error(
                f"Unable to activate shop {sitename}. Unhandled reason: {e}."
            )  # noqa: E501

    email = session.get("email", current_app.config["MAIL_DEFAULT_SENDER"])

    if is_donation is False:
        # TODO if checkout_session_id is None (because free plan)
        subscription = (
            database.session.query(Subscription)
            .execution_options(
                include_archived=True
            )  # To account for plans editing during checkout session starts
            .filter_by(subscribie_checkout_session_id=checkout_session_id)
            .first()
        )
        uuid = subscription.uuid
        # Store note to seller if in session
        if session.get("note_to_seller", False):
            note = SubscriptionNote(
                note=session["note_to_seller"], subscription_id=subscription.id
            )
            database.session.add(note)

        # Signal that a new subscriber has signed up
        signal_new_subscriber.send(
            current_app._get_current_object(), subscription_uuid=uuid
        )
    else:
        uuid = None
        # Send signal_new_donation, see receivers.py
        signal_new_donation.send(current_app._get_current_object(), email=email)
    database.session.commit()

    # Send journey_complete signal
    # Note: "journey_complete" is more generic than a donation or
    # a subscriber. journey_complete means a flow has been completed,
    # usually payment, but could involve a free plan for example.
    # See receivers.py for all signals
    # Trigger journey_complete, so that receivers will react.
    signal_journey_complete.send(
        current_app._get_current_object(),
        email=email,
        is_donation=is_donation,
        subscription_uuid=uuid,
    )

    return return_thankyou_page()


@checkout.route("/stripe-create-checkout-session", methods=["POST"])
def stripe_create_checkout_session():
    data = request.json
    is_donation = False
    plan = None
    charge = {}
    metadata = {}
    # Store the fact the person at least attempted to go to stripe
    # checkout (https://github.com/Subscribie/subscribie/issues/1370)
    # so that can distinguish between drop-offs before or after attempting
    # payment via checkout flow.

    # Store stripe_checkout_attempted True or similar against
    # subscription object using subscribie_checkout_session_id
    # to determine subscription object
    email = session["email"]
    subscribie_checkout_session_id = session.get("subscribie_checkout_session_id")
    subscription = (
        Subscription.query.filter_by(
            subscribie_checkout_session_id=subscribie_checkout_session_id
        )
        .filter(Subscription.person.has(email=email))
        .first()
    )
    if subscription is not None:
        subscription.stripe_user_attempted_checkout_flow = True
        database.session.commit()
        log.info(
            "Updated subscription object with stripe_user_attempted_checkout_flow: True"
        )
    else:
        msg = "Could not locate subscription during stripe_create_checkout_session"
        log.error(msg)

    currency_code = get_geo_currency_code()
    # If VAT tax is enabled, get stripe tax id
    settings = Setting.query.first()
    charge_vat = settings.charge_vat
    create_stripe_tax_rate()
    tax_rate = (
        TaxRate.query.filter_by(stripe_livemode=get_stripe_livemode())
        .order_by(TaxRate.id.desc())
        .first()
    )
    tax_rates = [tax_rate.stripe_tax_rate_id] if charge_vat is True else []
    person = Person.query.get(session["person_id"])
    charge["currency"] = currency_code
    payment_method_types = ["card"]
    cancel_url = url_for("checkout.order_summary", _external=True)
    mode = "payment"
    payment_intent_data = {}
    # Build line_items array depending on plan requirements
    line_items = []
    if session["is_donation"] is True:
        is_donation = True
        payment_intent_data = {
            "metadata": {
                "is_donation": is_donation,
                "person_uuid": person.uuid,
                "donation_comment": session["donation_comment"],
            }
        }

    # Add note to seller if present directly on payment metadata
    if session.get("note_to_seller", False):
        metadata["note_to_seller"] = session.get("note_to_seller")

    if is_donation is False:
        payment_intent_data = {"application_fee_amount": 20, "metadata": metadata}

        plan = (
            Plan.query.execution_options(include_archived=True)
            .filter_by(uuid=session["plan"])
            .first()
        )
        charge["sell_price"] = plan.getSellPrice(currency_code)
        charge["interval_amount"] = plan.getIntervalAmount(currency_code)
        success_url = url_for(
            "checkout.instant_payment_complete", _external=True, plan=plan.uuid
        )

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
                    "is_donation": is_donation,
                    "subscribie_checkout_session_id": session.get(
                        "subscribie_checkout_session_id", None
                    ),
                },
            }

            if plan.trial_period_days > 0:
                subscription_data["trial_period_days"] = plan.trial_period_days

        if plan.requirements.instant_payment:
            payment_intent_data = {
                "application_fee_amount": 20,
                "metadata": {"is_donation": is_donation, "person_uuid": person.uuid},
            }
        if plan.requirements.subscription:
            mode = "subscription"

            if charge_vat and is_donation is False:
                subscription_data["default_tax_rates"] = [tax_rate.stripe_tax_rate_id]
                # Add note to seller if present on subscription_data metadata
            if session.get("note_to_seller", False):
                subscription_data["metadata"]["note_to_seller"] = session.get(
                    "note_to_seller"
                )
            # Add trial period if present
            if plan.days_before_first_charge and plan.days_before_first_charge > 0:
                subscription_data["trial_period_days"] = plan.days_before_first_charge

        if plan.requirements.subscription:
            line_items.append(
                {
                    "price_data": {
                        "recurring": {
                            "interval": format_to_stripe_interval(plan.interval_unit)
                        },
                        "currency": charge["currency"],
                        "product_data": {"name": plan.title},
                        "unit_amount": charge["interval_amount"],
                    },
                    "quantity": 1,
                }
            )
        # Add line item for instant_payment if required
        if plan.requirements.instant_payment:
            # Append "Up-front fee" to product name if also a subscription
            plan_name = plan.title
            if plan.requirements.subscription:
                plan_name = "(Up-front fee) " + plan_name

            line_items.append(
                {
                    "tax_rates": tax_rates,
                    "price_data": {
                        "currency": charge["currency"],
                        "product_data": {"name": plan_name},
                        "unit_amount": charge["sell_price"],
                    },
                    "quantity": 1,
                }
            )

    elif is_donation is True:
        success_url = url_for("checkout.instant_payment_complete", _external=True)
        donation_amount = int(session["donation_amount"] * 100)
        line_items.append(
            {
                "price_data": {
                    "currency": charge["currency"],
                    "product_data": {"name": "Donation"},
                    "unit_amount": donation_amount,
                },
                "quantity": 1,
            }
        )

    stripe.api_key = get_stripe_secret_key()

    try:
        plan_uuid = session["plan"]
    except KeyError:
        log.warning("KeyError when generating stripe checkout session")
        log.warning(f"is_donation was set to: {is_donation}")
        plan_uuid = None

    metadata = {
        "person_uuid": person.uuid,
        "plan_uuid": plan_uuid,
        "chosen_option_ids": json.dumps(session.get("chosen_option_ids", None)),
        "chosen_question_ids_answers": json.dumps(
            session.get("chosen_question_ids_answers", None)
        ),  # noqa
        "package": session.get("package", None),
        "subscribie_checkout_session_id": session.get(
            "subscribie_checkout_session_id", None
        ),
        "is_donation": is_donation,
    }
    # Create Stripe checkout session for in payment or subscription mode
    if is_donation:
        log.info("Creating Stripe checkout session for a donation")
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
    elif plan.requirements.subscription:
        log.info("Creating Stripe checkout session for a new subscription")
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
        log.info("Creating Stripe checkout session for an instant payment")
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
    currency=None,  # None to allow subscriptions with no monetary association
    email=None,
    package=None,
    chosen_option_ids=None,
    chosen_question_ids_answers=None,
    subscribie_checkout_session_id=None,
    stripe_external_id=None,
    stripe_subscription_id=None,
) -> Subscription:
    """Create subscription model
    Note: A subscription model is also created if a plan only has
    one up_front payment (no recurring subscription). This allows
    the storing of chosen options against their plan choice.
    Chosen option ids may be passed via webhook or through session
    """
    with current_app.test_request_context("/"):  # TODO remove need for request context
        log.info("Creating Subscription model if needed")
        subscription = None  # Initialize subscription model to None
        # Get the associated plan they have purchased
        plan = (
            Plan.query.execution_options(include_archived=True)
            .order_by(desc("created_at"))
            .where(Plan.uuid == package)
            .one()
        )

        if currency is not None:
            sell_price, interval_amount = plan.getPrice(currency)
        else:
            log.warning(
                "currency was set to None, so setting Subscription sell_price and interval_amount to zero"  # noqa: E501
            )
            sell_price = 0
            interval_amount = 0

        # Store Subscription against Person locally
        # TODO enforce unique email address per Person object
        person = database.session.query(Person).filter_by(email=email).all()[0]

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
            log.info(
                "No existing subscription model found, creating Subscription model"
            )
            # Create new subscription model
            # - Get current pricing
            # - TODO address race condition:
            #   - add validation for potential discrepancy between Stripe
            #     webhook delivery delay and price rules changing
            subscription = Subscription(
                sku_uuid=package,
                person=person,
                subscribie_checkout_session_id=subscribie_checkout_session_id,
                stripe_external_id=stripe_external_id,
                stripe_subscription_id=stripe_subscription_id,
                interval_unit=plan.interval_unit,
                interval_amount=interval_amount,
                sell_price=sell_price,
                currency=currency,
            )
            database.session.add(subscription)
            # Add question answers (if any)
            answers = []
            if chosen_question_ids_answers:
                for answer in chosen_question_ids_answers:
                    question_id = answer["question_id"]
                    answer_response = answer["answer"]
                    question = Question.query.get(question_id)
                    if question is not None:
                        # We will store Question responses as Answer
                        # because Question.title may change after the order
                        # has processed. This preserves integrity of the actual
                        # answered questions
                        answer = Answer()
                        answer.question_id = question_id
                        answer.question_title = question.title
                        answer.response = answer_response
                        database.session.add(answer)
                        answers.append(answer)
            subscription.question_answers = answers

            # Add chosen options (if any)
            if chosen_option_ids and chosen_option_ids != "null":
                log.info(
                    f"Applying chosen_option_ids to subscription: {chosen_option_ids}"
                )
                chosen_options = []
                for option_id in chosen_option_ids:
                    log.info(f"Locating option id: {option_id}")
                    option = Option.query.get(option_id)
                    # Store as ChosenOption because options may change after the order
                    # has processed. This preserves integrity of the actual
                    # chosen options
                    chosen_option = ChosenOption()
                    if option is not None:
                        chosen_option.option_title = option.title
                        chosen_option.choice_group_title = option.choice_group.title
                        chosen_option.choice_group_id = (
                            option.choice_group.id
                        )  # Used for grouping latest choice
                        chosen_options.append(chosen_option)
                    else:
                        log.error(
                            f"Failed to get Open from session option_id: {option_id}"
                        )
                subscription.chosen_options = chosen_options
            else:
                log.info("No chosen_option_ids were found or applied.")

            database.session.commit()
            session["subscription_uuid"] = subscription.uuid

            # If subscription plan has cancel_at set
            # we can set subscription.plan.cancel_at right now without
            # needing to call Stripe api yet.
            # Note fore free plans, there's no Stripe subscription
            # object to modify for Subscribie free plans
            # When the Stripe subscription webhook is sent,
            # subscription will exist in Subscribie's datamodel
            # (subscription != None) and the Stripe api will be called
            # asynchronously to stripe api modify the stripe subscription
            # object with the cancel_at value.
            if subscription.plan.cancel_at:
                cancel_at = subscription.plan.cancel_at
                subscription.stripe_cancel_at = cancel_at
            database.session.commit()

    # Clear chosen_question_ids_answers from session since we've now stored them
    # Ref https://github.com/Subscribie/subscribie/issues/1374
    session.pop("chosen_question_ids_answers", None)
    return subscription


@backoff.on_exception(backoff.expo, Exception, max_tries=20)
def stripe_process_event_payment_intent_succeeded(event):
    """Store suceeded payment_intents as transactions
    Stripe sends Subscribie events of different types.
    This metod processes the payment_intent_succeeded event.
    This event will fire both at the begining of a subscription,
    and also at each successful recuring billing cycle.

    We use backoff because webhook event order from Stripe is not guaranteed,
    for example a `payment_intent_succeeded` event can be received before a
    `checkout.session.completed` event. If that happens, then the associated
    subscription may not be created yet in Subscribie database.
    Therefore the @backoff.on_exception allows processing of the
    payment_intent_succeeded event to retry until the
    checkout.session.completed event is processed.
    If the backoff fails (max_tries is exceeded) then Stripe will
    retry the event at a later time.

    Finally, refresh stripe invoices cache (via get_stripe_invoices)

    See also
    - https://stripe.com/docs/api/events/types#event_types-checkout.session.completed
    - https://stripe.com/docs/api/events/types#event_types-payment_intent.succeeded

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
        # There is no subscribie metadata on the event if its an upfront payment
        # So try and get it via the data['invoice'] attribute
        invoice_id = data["invoice"]

        # Stripe payment_intent invoice attribute may be null if
        # the payment intent is an instant charge (meaning not part of a
        # subscrtiption or plan).
        if invoice_id is not None:
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
        else:
            # If instance charge (not a subscription)
            # there is no checkout session (instant charge)
            subscribie_checkout_session_id = data["id"]
    except Exception as e:
        msg = f"Unable to get subscribie_checkout_session_id from event\n{e}"
        log.error(msg)
        return msg, 500
    try:
        metadata = data["metadata"]
        is_donation = metadata["is_donation"]
    except KeyError:
        # subscription doesnt have the "is_donation" inside the metadata
        # Locate the Subscribie subscription by its subscribie_checkout_session_id
        is_donation = False
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
        transaction.currency = data["currency"]
        transaction.amount = data["amount"]
        transaction.payment_status = (
            "paid" if data["status"] == "succeeded" else data["status"]
        )
        transaction.external_id = data["id"]
        transaction.external_src = "stripe"
        # this happens when is a subscription
        if subscribie_subscription is not None:
            transaction.person = subscribie_subscription.person
            transaction.subscription = subscribie_subscription
            transaction.is_donation = False
        # this happens when is one-off
        elif is_donation == "False" and subscribie_subscription is None:
            transaction.is_donation = False
            transaction.person = Person.query.filter_by(
                uuid=metadata["person_uuid"]
            ).one()
        # this happens when is a donation
        elif subscribie_subscription is None and is_donation == "True":
            transaction.person = Person.query.filter_by(
                uuid=metadata["person_uuid"]
            ).one()
            transaction.is_donation = True
            transaction.comment = metadata["donation_comment"]
        elif metadata == {}:
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
    # Refresh stripe invoices cache
    get_stripe_invoices()  # non-blocking
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
    is_donation = False
    company = Company.query.first()

    stripe_livemode = PaymentProvider.query.first().stripe_livemode
    if stripe_livemode != event["livemode"]:
        log.warning(
            f"Received a Stripe webhook event in a different livemode: {event['livemode']},  to the livemode currently set: '{stripe_livemode}'"  # noqa: E501
        )

    log.info(f"Received stripe webhook event type {event['type']}")

    if event["type"] == "customer.subscription.deleted":
        eventObj = event["data"]["object"]
        cancellation_reason = eventObj["cancellation_details"]["reason"]
        if cancellation_reason == "payment_failed":
            log.info(
                f"Subscription has been automatically cancelled. Reason code: {cancellation_reason}, possibly due to hardship"  # noqa: E501
            )
        elif cancellation_reason == "cancellation_requested":
            log.info(
                f"Subscription has been cancelled upon request. Reason code: {cancellation_reason}"  # noqa: E501
            )

        # Attempt to locate person associated with the Subscription
        person = None
        try:
            person_uuid = eventObj["metadata"]["person_uuid"]
            person = Person.query.filter_by(uuid=person_uuid).one()
        except Exception:
            log.error(
                "Unable to locate person associated with event customer.subscription.deleted"  # noqa: E501
            )

        # Attempt to locate plan associated with customer.subscription.deleted event
        plan = None
        try:
            plan_uuid = eventObj["metadata"]["plan_uuid"]
            plan = (
                Plan.query.execution_options(include_archived=True)
                .filter_by(uuid=plan_uuid)
                .one()
            )
        except Exception:
            log.error(
                "Unable to locate plan associated with event customer.subscription.deleted"  # noqa: E501
            )

        # Attempt to locate subscription association with customer.subscription.deleted
        # event
        subscription = None
        try:
            subscribie_checkout_session_id = eventObj["metadata"][
                "subscribie_checkout_session_id"
            ]
            subscription = (
                # Include archived to account for plan edits during an active checkout
                Subscription.query.execution_options(include_archived=True)
                .filter_by(
                    subscribie_checkout_session_id=subscribie_checkout_session_id
                )
                .one()
            )
        except Exception:
            log.error(
                "Unable to locate subscription associated with event customer.subscription.deleted"  # noqa: E501
            )

        if person is not None:
            subject = (
                f"{company.name}: A Subscription has ended for: {person.given_name}"
            )
            # Send email notification to shop owner about subscription ending
            emailBody = (
                f"A Subscription has ended for: {person.given_name}\n\n"
                f"Email: {person.email}\n\n"
                f"The reason code for the cancellation was: {cancellation_reason}\n"
            )

            if cancellation_reason == "payment_failed":
                emailBody += (
                    "Given the reason code was payment_failed, this means multiple "
                    "attempts to collect this payment have failed, and the "
                    "subscription has therefore been cancelled.\n\n"
                    "Please reach out to the person where possible to resolve.\n\n"
                    "You can find further details by logging into your shop, and "
                    "clicking 'subscription cancellations' under 'Stats'."
                )
            log.info(emailBody)
        else:
            subject = f"A Subscription has ended for: {person.given_name}"
            emailBody = (
                "A subscription has just ended.\n\n"
                "Login to your shop dashboard and click"
                "'subscription cancellations' under 'Stats' for details."
            )

        if plan is not None:
            emailBody += "\n\nThe plan title was:\n" f"{plan.title}"

        if subscription is not None:
            if subscription.note is not None and subscription.note.note != "":
                emailBody += (
                    "When the subscriber originally signed-up, "
                    "they provided the following note:\n\n"
                    f'"{subscription.note.note}"'
                )

        shop_admins = [user.email for user in User.query.all()]
        msg = EmailMessageQueue()
        msg["Subject"] = subject
        msg["FROM"] = current_app.config["EMAIL_LOGIN_FROM"]
        msg["TO"] = shop_admins
        msg.set_content(emailBody)
        msg.queue()
        return "OK", 200

    # Handle the payment_intent.payment_failed
    if event["type"] == "payment_intent.payment_failed":
        log.info("Stripe webhook event: payment_intent.payment_failed")
        try:
            eventObj = event["data"]["object"]
            log.info(eventObj)
            personName = eventObj["charges"]["data"][0]["billing_details"]["name"]
            personEmail = eventObj["charges"]["data"][0]["billing_details"]["email"]
            # Notify Shop owner if payment_failed event was related to a Subscription charge # noqa: E501
            if eventObj["charges"]["data"][0]["description"] == "Subscription update":
                emailBody = f"""A recent subscription charge failed to be collected from Subscriber:\n\n{personName}\n\nEmail: {personEmail}\n\n
                The failure code was: {eventObj['charges']['data'][0]['failure_code']}\n\n
                The failure message was: {eventObj['charges']['data'][0]['failure_message']}\n\n
                Please note, payments are automatically retried and no action is required unless you wish to pause or stop the subscription from your admin dashboard."""  # noqa: E501
                log.info(emailBody)
                shop_admins = [user.email for user in User.query.all()]
                company = Company.query.first()
                msg = EmailMessageQueue()
                msg["Subject"] = company.name + " " + "A payment collection failed"
                msg["FROM"] = current_app.config["EMAIL_LOGIN_FROM"]
                msg["TO"] = shop_admins
                msg.set_content(emailBody)
                msg.queue()
            # Signal that a Stripe payment_intent.payment_failed event has been received, # noqa: E501
            # so that receivers (such as notify Subscriber) are notified
            signal_payment_failed.send(stripe_event=eventObj)
        except Exception as e:
            log.error(f"Unhandled error processing payment_intent.payment_failed: {e}")
        return "OK", 200
    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        log.info("Processing checkout.session.completed event")
        if event["data"]["object"]["mode"] == "setup":
            log.info("checkout.session.completed mode is setup, returning 200 OK early")
            return "OK", 200

        session = event["data"]["object"]
        currency = session["currency"].upper()
        email = session["customer_email"]
        try:
            is_donation = session["metadata"]["is_donation"]
        except KeyError as e:
            log.error(
                f"Could not identify if Stripe metadata was is_donation or not. {e}"
            )
        if is_donation is True:
            subscribie_checkout_session_id = session["id"]
        else:
            try:
                subscribie_checkout_session_id = session["metadata"][
                    "subscribie_checkout_session_id"
                ]
            except KeyError as e:
                subscribie_checkout_session_id = None
                log.warning(
                    f"Could not get subscribie_checkout_session_id from session metadata in webhook checkout.session.completed: {e}"  # noqa: E501
                )
                log.warning(
                    f"The provided metadata (if any) was: {session['metadata']}"
                )

        if session["mode"] == "subscription":
            stripe_subscription_id = session["subscription"]
        else:
            stripe_subscription_id = None

        try:
            chosen_option_ids = session["metadata"]["chosen_option_ids"]
            chosen_option_ids = json.loads(chosen_option_ids)
        except KeyError:
            chosen_option_ids = None

        # Set proration_behavior if is a subscription
        # https://github.com/Subscribie/subscribie/issues/1133
        # TODO proration_behavior should be set regarless of
        # payment provider.
        if stripe_subscription_id:
            subscription = (
                # Include archived to account for plan edits during an active checkout
                Subscription.query.execution_options(include_archived=True)
                .filter_by(
                    subscribie_checkout_session_id=subscribie_checkout_session_id
                )
                .filter(Subscription.person.has(email=email))
                .first()
            )
            if subscription is not None:
                stripe.api_key = get_stripe_secret_key()
                connect_account_id = get_stripe_connect_account_id()

                # If subscription's plan has a cancel_at date, and is not free
                # update the Stripe subscription object to set the cancel_at
                # field.
                # Note: subscription.stripe_cancel_at is set before the Stripe
                # subscription object is created, before calls to stripe
                # api hence why we update Stripe's datamodel here.
                if subscription.plan.cancel_at and subscription.plan.is_not_free():
                    log.info("Setting Stripe subscription object cancel_at property")
                    try:
                        stripe.Subscription.modify(
                            id=stripe_subscription_id,
                            stripe_account=connect_account_id,
                            cancel_at=subscription.stripe_cancel_at,
                        )
                    except Exception as e:
                        log.error(
                            f"Could not set cancel_at on Stripe subscription object: {e}"  # noqa: E501
                        )
                    database.session.commit()

                proration_behavior = subscription.plan.proration_behavior or "none"
                log.info(
                    f"Updating stripe proration_behavior to {proration_behavior}"
                )  # noqa: E501
                try:
                    stripe.Subscription.modify(
                        stripe_subscription_id,
                        stripe_account=connect_account_id,
                        proration_behavior=proration_behavior,
                    )
                    # Set the local db model stripe_proration_behavior
                    subscription.stripe_proration_behavior = proration_behavior
                    database.session.commit()
                except Exception as e:  # noqa
                    log.error(
                        "Could not update proration_behavior: '{e}' for stripe_subscription_id {stripe_subscription_id}"  # noqa: E501
                    )

        """
        We treat Stripe checkout session.mode equally because
        a subscribie plan may either be a one-off plan or a
        recuring plan. A 'subscription' is still created in the
        subscribie database regardless of if the Stripe session
        mode is "payment" or "subscription".
        See https://stripe.com/docs/api/checkout/sessions/object
        """
        if is_donation != "True":
            if session["mode"] == "subscription" or session["mode"] == "payment":
                # Rather than call create_subscription here (as we used to do)
                # https://github.com/Subscribie/subscribie/issues/1370
                # Instead, locate the existing subscription object (which are created
                # irrespective of payments) by it's subscribie_checkout_session_id
                # which will be stored in the payment providers webhook metadata
                # and update the subscription object with the currency of the payment,
                # and relevant Payment
                # provider checkout attributes (such as `stripe_subscription_id`
                # and `stripe_external_id`) for Stripe.
                subscription = (
                    Subscription.query.filter_by(
                        subscribie_checkout_session_id=subscribie_checkout_session_id
                    )
                    .filter(Subscription.person.has(email=email))
                    .first()
                )
                if subscription is not None:
                    subscription.stripe_subscription_id = stripe_subscription_id
                    subscription.stripe_external_id = session["id"]
                    subscription.currency = currency
                    database.session.commit()
                    msg = f"Updated subscription object with stripe_subscription_id: {stripe_subscription_id} and stripe_external_id {session['id']}"  # noqa: E501
                    log.info(msg)
                else:
                    msg = "Webhook event failure. Could not locate subscription object for checkout.session.completed event."  # noqa: E501
                    log.error(msg)
                    return msg, 500
        return "OK", 200

    if (
        stripe_livemode == event["livemode"]
        and event["type"] == "payment_intent.succeeded"
    ):
        return stripe_process_event_payment_intent_succeeded(event)

    msg = {"msg": "Unknown event", "event": event}
    log.debug(msg)

    return jsonify(msg), 422
