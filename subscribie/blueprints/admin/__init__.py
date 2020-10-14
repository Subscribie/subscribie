from flask import Blueprint, render_template, abort, flash, json, send_from_directory, g
import jinja2
from jinja2 import TemplateNotFound, Markup, Environment
from subscribie import (
    database,
    logging,
    session,
    render_template,
    request,
    redirect,
    gocardless_pro,
    GocardlessConnectForm,
    StripeConnectForm,
    ChangePasswordForm,
    ChangeEmailForm,
    AddShopAdminForm,
    current_app,
    redirect,
    url_for,
    GoogleTagManagerConnectForm,
    PlansForm,
    jsonify,
    TawkConnectForm,
    database, User, Person, Subscription, SubscriptionNote, Company,
    Integration, PaymentProvider, Plan, PlanRequirements, PlanSellingPoints
)
from subscribie.forms import UploadLogoForm, WelcomeEmailTemplateForm, SetReplyToEmailForm, UploadFilesForm
from subscribie.auth import login_required, protected_download
from subscribie.db import get_db
from subscribie.symlink import symlink
import yaml
from flask_uploads import configure_uploads, UploadSet, IMAGES
import os, sys
from pathlib import Path
from .getLoadedModules import getLoadedModules
import subprocess
import uuid
from sqlalchemy import asc, desc
from datetime import datetime
from subscribie.models import ChoiceGroup, Transaction, EmailTemplate, Setting, File
import stripe
from werkzeug.utils import secure_filename


admin = Blueprint(
    "admin", __name__, template_folder="templates", static_folder="static"
)

from .choice_group import list_choice_groups
from .option import list_options
from .subscriber import show_subscriber

@admin.app_template_filter()
def currencyFormat(value):
  value = float(value)/100
  return "£{:,.2f}".format(value)


def store_gocardless_transaction(gocardless_payment_id):
    """Store GoCardless payment in transactions table"""
    payment_provider = PaymentProvider.query.first()
    gocclient = gocardless_pro.Client(
      access_token=payment_provider.gocardless_access_token,
          environment=payment_provider.gocardless_environment,
    )
    payment = gocclient.payments.get(gocardless_payment_id)

    # Check if there's an existing payment record in transactions table
    transaction = Transaction.query.filter_by(external_id=gocardless_payment_id).first()
    if transaction is None:
        # No existing transaction found, so fetch payment info from GoCardless
        # Store as transaction
        transaction = Transaction()
        transaction.amount = payment.amount
        transaction.payment_status = payment.status
        transaction.comment = str(payment.metadata)
        transaction.external_id = gocardless_payment_id
        transaction.external_src = "gocardless"
        # Find related subscription if exists
        if payment.links.subscription:
            subscription_id = payment.links.subscription
            subscription = Subscription.query.filter_by(gocardless_subscription_id=subscription_id).first()
            if subscription is not None:
                transaction.subscription = subscription
            try:
                transaction.person = subscription.person
            except AttributeError: # A transaction may not have a person
                pass

    # Update payment_status to gocardless latest status
    transaction.payment_status = payment.status

    database.session.add(transaction)
    database.session.commit() # Save/update transaction in transactions table
    return transaction


@admin.route("payments/update/<gocardless_payment_id>")
@login_required
def update_payment_fulfillment(gocardless_payment_id):
    """Update payment fulfillment stage"""

    transaction = Transaction.query.filter_by(external_id=gocardless_payment_id).first()
    if transaction is None:
        transaction = store_gocardless_transaction(gocardless_payment_id)

    # Update transactions fulfillment_state to the value specified
    fulfillment_state = request.args.get('state', '')
    # Check a valid fulfillment_state is passed (only one or empty at the moment)
    if fulfillment_state == '' or fulfillment_state == 'complete':
        transaction.fulfillment_state = fulfillment_state
        flash("Fulfillment state updated")

    database.session.add(transaction)
    database.session.commit() # Save/update transaction in transactions table

    # Go back to previous page
    return redirect(request.referrer)

@admin.route("/gocardless/subscriptions/<subscription_id>/actions/pause")
@login_required
def pause_gocardless_subscription(subscription_id):
    """Pause a GoCardless subscription"""
    payment_provider = PaymentProvider.query.first()        
    gocclient = gocardless_pro.Client(
      access_token=payment_provider.gocardless_access_token,
          environment=payment_provider.gocardless_environment,
    )

    try:
        req = gocclient.subscriptions.pause(subscription_id)
    except gocardless_pro.errors.InvalidStateError as e:
        return jsonify(error=e.message)

    flash("Subscription paused")

    if 'goback' in request.args:
        return redirect(request.referrer)
    return jsonify(message="Subscription paused", subscription_id=subscription_id)

@admin.route("/gocardless/subscriptions/<subscription_id>/actions/resume")
@login_required
def resume_gocardless_subscription(subscription_id):
    """Resume a GoCardless subscription"""
    payment_provider = PaymentProvider.query.first()        
    gocclient = gocardless_pro.Client(
      access_token=payment_provider.gocardless_access_token,
          environment=payment_provider.gocardless_environment,
    )

    try:
        req = gocclient.subscriptions.resume(subscription_id)
    except gocardless_pro.errors.InvalidStateError as e:
        return jsonify(error=e.message)

    flash("Subscription resumed")

    if 'goback' in request.args:
        return redirect(request.referrer)

    return jsonify(message="Subscription resumed", subscription_id=subscription_id)

@admin.route("/cancel/mandates/<email>")
@login_required
def cancel_mandates(email):
  """Cancel all mandates associated with a given email"""
  if "confirm" in request.args:
    # Get all mandates associated with <email>
    # Then cancel them
    transactions = get_transactions()
    partner_madates = []
    for transaction in transactions:
      # Match email to mandates
      if transaction.mandate['links']['customer']['email'] == email \
      and transaction.mandate['status'] == 'active':
        partner_madates.append(transaction.mandate)
    
    if len(partner_madates) > 0:
      payment_provider = PaymentProvider.query.first()        
      gocclient = gocardless_pro.Client(
        access_token=payment_provider.gocardless_access_token,
        environment=payment_provider.gocardless_environment,
      )

      for mandate in partner_madates: # Cancel each mandate for given email
        removed = False
        try:
          req = gocclient.mandates.cancel(mandate['id'])
          flash("Mandate canceled for {}".format(email))
          flash("The mandate ID was: {}".format(mandate['id']))
          removed = True
        except gocardless_pro.errors.InvalidStateError:
          removed = True
          flash("Mandate already canceled for {}".format(email))
          flash("The mandate ID was: {}".format(mandate['id']))

        if removed:
          # Remove from local mandates list
          refresh_ssot(resource='customers')
          
      return redirect(url_for("admin.customers"))
  return render_template("admin/cancel_mandates_confirm.html", email=email)

@admin.route("/dashboard")
@login_required
def dashboard():
    integration = Integration.query.first()
    payment_provider = PaymentProvider.query.first()
    if payment_provider is None:
        # If payment provider table is not seeded, seed it now with blank values.
        payment_provider = PaymentProvider()
        database.session.add(payment_provider)
        database.session.commit()
    if payment_provider.gocardless_active:
        gocardless_connected = True
    else:
        gocardless_connected = False
    if payment_provider.stripe_active:
        stripe_connected = True
    else:
        stripe_connected = False
    return render_template(
        "admin/dashboard.html",
        gocardless_connected=gocardless_connected,
        stripe_connected=stripe_connected,
        integration=integration,
        loadedModules=getLoadedModules()
    )


@admin.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit plans
    
    Note plans are immutable, when a change is made to plan, its old
    plan is archived and a new plan is created with a new uuid. This is to
    protect data integriry and make sure plan history is retained, via its uuid.
    If a user needs to change a subscription, they should change to a different
    plan with a different uuid.

    """

    form = PlansForm()
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    if form.validate_on_submit():
        company = Company.query.first()
        company.name  = request.form["company_name"]
        company.slogan = request.form["slogan"]
        # Loop plans
        for index in request.form.getlist("planIndex", type=int):

            # Archive existing plan then create new plan
            # (remember, edits create new plans because
            # plans are immutable)
            plan = Plan.query.filter_by(uuid=form.uuid.data[index]).first()
            plan.archived = True

            # Build new plan
            draftPlan = Plan()
            database.session.add(draftPlan)
            plan_requirements = PlanRequirements()

            draftPlan.uuid = str(uuid.uuid4())
            draftPlan.requirements = plan_requirements
            # Preserve primary icon if exists
            draftPlan.primary_icon = plan.primary_icon

            # Preserve choice_groups
            draftPlan.choice_groups = plan.choice_groups

            draftPlan.title = getPlan(
                form.title.data, index, default=""
            ).strip()

            draftPlan.position = getPlan(
                form.position.data, index
            )

            if getPlan(form.subscription.data, index) == 'yes':
                plan_requirements.subscription = True
            else:
                plan_requirements.subscription = False

            interval_unit = getPlan(
                    form.interval_unit.data, index, default=""
            )
            if 'monthly' in interval_unit or 'yearly' in interval_unit or \
               'weekly' in interval_unit:
                   draftPlan.interval_unit = interval_unit

            if getPlan(form.interval_amount.data, index, default=0) is None:
                interval_amount = 0
            else:
                interval_amount = int(getPlan(form.interval_amount.data, index, default=0) * 100)
            draftPlan.interval_amount = interval_amount
            if getPlan(form.instant_payment.data, index) == 'yes':
                plan_requirements.instant_payment = True
            else:
                plan_requirements.instant_payment = False

            if getPlan(form.note_to_seller_required.data, index) == 'yes':
                plan_requirements.note_to_seller_required = True
            else:
                plan_requirements.note_to_seller_required = False

            plan_requirements.note_to_buyer_message = str(getPlan(
                form.note_to_buyer_message, index, default=""
            ).data)

            try:
                days_before_first_charge = int(form.days_before_first_charge[index].data)
            except ValueError:
                days_before_first_charge = 0

            draftPlan.days_before_first_charge = days_before_first_charge

            if getPlan(form.sell_price.data, index, default=0) is None:
                sell_price = 0
            else:
                sell_price = int(getPlan(form.sell_price.data, index, default=0) * 100)

            draftPlan.sell_price = sell_price

            points = getPlan(
                form.selling_points.data, index, default=""
            )
            for point in points:
                draftPlan.selling_points.append(PlanSellingPoints(point=point))

            # Primary icon image storage
            f = getPlan(form.image.data, index)
            if f:
                images = UploadSet("images", IMAGES)
                filename = images.save(f)
                # symlink to active theme static directory
                img_src = "".join(
                    [current_app.config["UPLOADED_IMAGES_DEST"], filename]
                )
                link = "".join([current_app.config["STATIC_FOLDER"], filename])
                symlink(img_src, link, overwrite=True)
                src = url_for("static", filename=filename)
                draftPlan.primary_icon = src
        database.session.commit() # Save
        flash("Plan(s) updated.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit.html", plans=plans, form=form)


@admin.route("/add", methods=["GET", "POST"])
@login_required
def add_plan():
    form = PlansForm()
    if form.validate_on_submit():
        draftPlan = Plan()
        database.session.add(draftPlan)
        plan_requirements = PlanRequirements()
        draftPlan.requirements = plan_requirements

        draftPlan.uuid = str(uuid.uuid4())
        draftPlan.title = form.title.data[0].strip()
        draftPlan.position = request.form.get('position-0', 0)
        interval_unit = form.interval_unit.data[0].strip()
        if 'monthly' in interval_unit or 'yearly' in interval_unit or \
           'weekly' in interval_unit:
               draftPlan.interval_unit = interval_unit

        if form.subscription.data[0] == 'yes':
            plan_requirements.subscription = True
        else:
            plan_requirements.subscription = False
        if form.note_to_seller_required.data[0] == 'yes':
            plan_requirements.note_to_seller_required = True
        else:
            plan_requirements.note_to_seller_required = False

        plan_requirements.note_to_buyer_message = str(form.note_to_buyer_message.data[0])
        try:
            days_before_first_charge = int(form.days_before_first_charge.data[0])
        except ValueError:
            days_before_first_charge = 0

        draftPlan.days_before_first_charge = days_before_first_charge

        if form.interval_amount.data[0] is None:
            draftPlan.interval_amount = 0
        else:
            draftPlan.interval_amount = int(form.interval_amount.data[0]) * 100

        if form.instant_payment.data[0] == 'yes':
            plan_requirements.instant_payment = True
        else:
            plan_requirements.instant_payment = False

        if form.sell_price.data[0] is None:
            draftPlan.sell_price = 0
        else:
            draftPlan.sell_price = int(form.sell_price.data[0]) * 100

        points = form.selling_points.data[0]

        for point in points:
            draftPlan.selling_points.append(PlanSellingPoints(point=point))

        # Primary icon image storage
        f = form.image.data[0]
        if f:
            images = UploadSet("images", IMAGES)
            filename = images.save(f)
            # symlink to active theme static directory
            img_src = "".join([current_app.config["UPLOADED_IMAGES_DEST"], filename])
            link = "".join([current_app.config["STATIC_FOLDER"], filename])
            os.symlink(img_src, link)
            src = url_for("static", filename=filename)
            draftPlan.primary_icon = src

        database.session.commit()
        flash("Plan added.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/add_plan.html", form=form)


@admin.route("/delete", methods=["GET"])
@login_required
def delete_plan():
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    return render_template("admin/delete_plan_choose.html", plans=plans)


@admin.route("/delete/<uuid>", methods=["GET", "POST"])
@login_required
def delete_plan_by_uuid(uuid):
    """Archive (dont actually delete) an plan"""
    plan = Plan.query.filter_by(uuid=uuid).first()

    if "confirm" in request.args:
        confirm = False
        return render_template(
            "admin/delete_plan_choose.html",
            confirm=False,
            plan=plan
        )
    if uuid is not False:
        # Perform archive
        plan.archived = True
        database.session.commit()

    flash("Plan deleted.")
    plans = Plan.query.filter_by(archived=0).all()
    return render_template("admin/delete_plan_choose.html", plans=plans)


@admin.route("/connect/gocardless/manually", methods=["GET", "POST"])
@login_required
def connect_gocardless_manually():
    payment_provider = PaymentProvider.query.first()        
    form = GocardlessConnectForm()
    if payment_provider.gocardless_active:
        gocardless_connected = True
    else:
        gocardless_connected = False
    if form.validate_on_submit():
        access_token = form.data["access_token"]
        payment_provider.gocardless_access_token = access_token
        # Check if live or test api key was given
        if "live" in access_token:
            payment_provider.gocardless_environment = "live"
        else:
            payment_provider.gocardless_environment = "sandbox"
        
        payment_provider.gocardless_active = True
        database.session.commit() # save changes

        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_gocardless_manually.html",
            form=form,
            gocardless_connected=gocardless_connected,
        )


@admin.route("/connect/gocardless", methods=["GET"])
@login_required
def connect_gocardless_start():
    flow = OAuth2WebServerFlow(
        client_id=current_app.config["GOCARDLESS_CLIENT_ID"],
        client_secret=current_app.config["GOCARDLESS_CLIENT_SECRET"],
        scope="read_write",
        redirect_uri="http://127.0.0.1:5000/connect/gocardless/oauth/complete",
        auth_uri="https://connect-sandbox.gocardless.com/oauth/authorize",
        token_uri="https://connect-sandbox.gocardless.com/oauth/access_token",
        initial_view="signup",
        prefill={
            "email": "tim@gocardless.com",
            "given_name": "Tim",
            "family_name": "Rogers",
            "organisation_name": "Tim's Fishing Store",
        },
    )
    authorize_url = flow.step1_get_authorize_url()
    return flask.redirect(authorize_url, code=302)

def getStripeAccount(account_id):
    if account_id is None:
     raise NameError("account_id is not set")
    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY", None)
    try:
        account = stripe.Account.retrieve(account_id)
    except stripe.error.PermissionError as e:
        print(e)
        raise
    except stripe.error.InvalidRequestError as e:
        print(e)
        raise
    except Exception as e:
        account = None

    return account

def create_stripe_webhook():
    """
    Creates a new webhook, deleting old one if present
    switching from test to live mode
    """
    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY", None)
    webhook_url = url_for('views.stripe_webhook',_external=True)
    payment_provider = PaymentProvider.query.first()

    liveMode = False
    webhookIdExists = False
    newWebhookNeeded = True

    if payment_provider.stripe_webhook_endpoint_id is not None:
        webhookIdExists = True

    # Determine if in live or test mode by inspecting api keys
    if (
        "live" in current_app.config.get("STRIPE_SECRET_KEY","")
        and "live" in current_app.config["STRIPE_PUBLISHABLE_KEY"]
    ):
        liveMode = True
    else:
        liveMode = False

    # Try to get current webhook and check if its in livemode
    if webhookIdExists:
        try:
            current_webhook = stripe.WebhookEndpoint.retrieve(payment_provider.stripe_webhook_endpoint_id)
            if current_webhook.livemode == liveMode:
                newWebhookNeeded = False
            else:
                stripe.WebhookEndpoint.delete(current_webhook.id)
                newWebhookNeeded = True

        except stripe.error.InvalidRequestError as e:
                newWebhookNeeded = True

    if newWebhookNeeded and "127.0.0.1" not in current_app.config.get("SERVER_NAME", ""):
        # Delete previous webhooks which match the webhook_url
        webhooks = stripe.WebhookEndpoint.list()
        for webhook in webhooks:
            if webhook.url == webhook_url:
                stripe.WebhookEndpoint.delete(webhook.id)

        # Create a new webhook
        try:
            webhook_endpoint = stripe.WebhookEndpoint.create(
              url = webhook_url,
              enabled_events=[
                "*",
              ],
              description = "Subscribie webhook endpoint",
              connect = True, # endpoint should receive events from connected accounts
            )
            # Store the webhook secret & webhook id
            payment_provider.stripe_webhook_endpoint_id = webhook_endpoint.id
            payment_provider.stripe_webhook_endpoint_secret = webhook_endpoint.secret
            payment_provider.stripe_livemode = liveMode
            print(f"New webhook id is: {payment_provider.stripe_webhook_endpoint_id}")
        except stripe.error.InvalidRequestError as e:
            print(e)
            flash("Error trying to create Stripe webhook")
            payment_provider.stripe_active = False
    database.session.commit()


@admin.route("/connect/stripe-connect", methods=["GET"])
@login_required
def stripe_connect():
    account = None
    stripe_express_dashboard_url = None
    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY", None)
    payment_provider = PaymentProvider.query.first()

    try:
        account = getStripeAccount(payment_provider.stripe_connect_account_id)
        if account is not None and account.charges_enabled and account.payouts_enabled:
            payment_provider.stripe_active = True
        else:
            payment_provider.stripe_active = False
    except (stripe.error.PermissionError, stripe.error.InvalidRequestError, NameError, AttributeError) as e:
        print(e)
        account = None

    # Setup Stripe webhook endpoint if it dosent already exist
    if account:
        try:
            stripe_express_dashboard_url = stripe.Account.create_login_link(account.id).url
        except stripe.error.InvalidRequestError:
            stripe_express_dashboard_url = None
        webhook_url = url_for('views.stripe_webhook',_external=True)
        if '127.0.0.1' not in request.host: # Dont create webhooks on localhost, use stripe cli for that
            create_stripe_webhook()
        else:
            print(f"Refusing to Stripe webhook on localhost: {webhook_url}")

    database.session.commit()
    return render_template('admin/settings/stripe/stripe_connect.html',
                            stripe_onboard_path=url_for('admin.stripe_onboarding'),
                            account=account,
                            stripe_express_dashboard_url=stripe_express_dashboard_url)

@admin.route("/stripe-onboard", methods=["POST"])
@login_required
def stripe_onboarding():

    stripe.api_key = current_app.config.get("STRIPE_SECRET_KEY", None)
    company = Company.query.first()

    # Try to use existing stripe_connect_account_id if present, otherwise create an account
    payment_provider = PaymentProvider.query.first()
    try:
        print("Trying if there's an existing stripe account")
        account = getStripeAccount(payment_provider.stripe_connect_account_id)
        print(f"Yes, stripe account found: {account.id}")
    except (stripe.error.PermissionError, stripe.error.InvalidRequestError, NameError, AttributeError):
        print("Could not find a stripe account, Creating stripe account")
        account = stripe.Account.create(type='express', email=g.user.email,
                                        default_currency='gbp',
                                        business_profile={'url': request.host_url,
                                                          'name': company.name
                                        },
                                        capabilities={
                                            'card_payments': {'requested': True},
                                            'transfers': {'requested': True},
                                        })
        payment_provider.stripe_connect_account_id = account.id
        database.session.commit()

    session['account_id'] = account.id

    account_link_url = _generate_account_link(account.id)
    try:
        return jsonify({'url': account_link_url})
    except Exception as e:
        return jsonify(error=str(e)), 403


def _generate_account_link(account_id):
    '''
    From the Stripe Docs:
    A user that is redirected to your return_url might not have completed the
    onboarding process. Use the /v1/accounts endpoint to retrieve the user’s
    account and check for charges_enabled. If the account is not fully onboarded,
    provide UI prompts to allow the user to continue onboarding later. The user
    can complete their account activation through a new account link (generated
    by your integration). You can check the state of the details_submitted
    parameter on their account to see if they’ve completed the onboarding process.
    '''
    account_link = stripe.AccountLink.create(
        type='account_onboarding',
        account=account_id,
        refresh_url=url_for('admin.stripe_connect', refresh="refresh", _external=True),
        return_url=url_for('admin.stripe_connect', success="success", _external=True),
    )
    return account_link.url

@admin.route('/stripe-onboard/refresh', methods=['GET'])
def onboard_user_refresh():
    if 'account_id' not in session:
        return redirect(url_for('admin.stripe_onboarding'))

    account_id = session['account_id']

    origin = ('https://' if request.is_secure else 'http://') + request.headers['host']
    account_link_url = _generate_account_link(account_id)
    return redirect(account_link_url)


@admin.route("/connect/google_tag_manager/manually", methods=["GET", "POST"])
@login_required
def connect_google_tag_manager_manually():
    integration = Integration.query.first()
    form = GoogleTagManagerConnectForm()
    if form.validate_on_submit():
        container_id = form.data["container_id"]
        integration.google_tag_manager_container_id = container_id
        integration.google_tag_manager_active = True
        database.session.commit()
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_google_tag_manager_manually.html", form=form,
            integration=integration
        )


@admin.route("/connect/tawk/manually", methods=["GET", "POST"])
@login_required
def connect_tawk_manually():
    integration = Integration.query.first()
    form = TawkConnectForm()
    if form.validate_on_submit():
        property_id = form.data["property_id"]
        integration.tawk_property_id = property_id
        integration.tawk_active = True
        database.session.commit()
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_tawk_manually.html", form=form, integration=integration
        )


@admin.route("/retry-payment/<payment_id>", methods=["GET"])
def retry_payment(payment_id):
    payment_provider = PaymentProvider.query.first()        
    gocclient = gocardless_pro.Client(
      access_token=payment_provider.gocardless_access_token,
          environment=payment_provider.gocardless_environment,
    )
    r = gocclient.payments.retry(payment_id)

    return "Payment (" + payment_id + " retried." + str(r)


@admin.route("/ssot/refresh/<resource>", methods=["GET"])
@login_required
def refresh_ssot(resource):
  """Refresh SSOT to fetch newest customers (aka partners) and transactions
  resource is either "customers" or "transactions"
  """
  payment_provider = PaymentProvider.query.first()
  access_token = payment_provider.gocardless_access_token
  gc_environment = payment_provider.gocardless_environment

  target_gateways = ({"name": "GoCardless", 
                                      "construct": {
                                        "access_token":access_token,
                                        "environment": gc_environment
                                        }
                                    },)
  try:
      SSOT = SSOT(target_gateways, refresh=True)
      partners = SSOT.partners
  except gocardless_pro.errors.InvalidApiUsageError as e:
      logging.error(e.type)
      logging.error(e.message)
      flash("Invalid GoCardless API token. Correct your GoCardless API key.")
      return redirect(url_for("admin.connect_gocardless_manually"))
  except ValueError as e:
      logging.error(e.message)
      if e.message == "No access_token provided":
          flash("You must connect your GoCardless account first.")
          return redirect(url_for("admin.connect_gocardless_manually"))
      else:
          raise
  if resource == "customers":
    flash("Customers refreshed")
    return redirect(url_for('admin.customers'))
  if resource == "transactions":
    flash("Customers refreshed")
    return redirect(url_for('admin.transactions'))
  # Fallback
  flask("Refreshed customers & transactions")
  return redirect(url_for('admin.dashboard'))

def get_transactions():
  """Return tuple list of transactions from SSOT"""
  from SSOT import SSOT
  payment_provider = PaymentProvider.query.first()
  access_token = payment_provider.gocardless_access_token
  gc_environment = payment_provider.gocardless_environment

  target_gateways = ({"name": "GoCardless", 
                                      "construct": {
                                        "access_token":access_token,
                                        "environment": gc_environment
                                        }
                                    },)
  try:
      SSOT = SSOT(target_gateways)
      transactions = SSOT.transactions
  except gocardless_pro.errors.InvalidApiUsageError as e:
      logging.error(e.type)
      logging.error(e.message)
      flash("Invalid GoCardless API token. Correct your GoCardless API key.")
      return redirect(url_for("admin.connect_gocardless_manually"))
  except ValueError as e:
      logging.error(e.message)
      if e.message == "No access_token provided":
          flash("You must connect your GoCardless account first.")
          return redirect(url_for("admin.connect_gocardless_manually"))
      else:
          raise
  return transactions
  

@admin.context_processor
def utility_gocardless_check_user_active():
  def is_active_gocardless(email):
    # Locate mandate IDs which contain customer email,
    # and cancel them.
    transactions = get_transactions()
    partner_madates = []
    for transaction in transactions:
      # Match email to mandate
      if transaction.mandate['links']['customer']['email'] == email \
      and transaction.mandate['status'] == 'active':
        partner_madates.append(transaction.mandate)
        return True
    return False
  return dict(is_active_gocardless=is_active_gocardless)

@admin.context_processor
def utility_gocardless_get_sku_uuid_from_gocardless_subscription_id():
  def get_sku_uuid_from_gocardless_subscription_id(subscription_id):
      """Get sku uuid from GoCardless subscription id"""
      try:
          subscription = Subscription.query.filter_by(gocardless_subscription_id=subscription_id).first()
          sku_uuid = subscription.sku_uuid 
      except AttributeError:
          return None
      return sku_uuid

  return dict(get_sku_uuid_from_gocardless_subscription_id=get_sku_uuid_from_gocardless_subscription_id)

@admin.context_processor
def utility_get_subscription_from_gocardless_subscription_id():
    """Return sqlalchemy Subscription object"""
    def get_subscription_from_gocardless_subscription_id(subscription_id):
        if subscription_id is None:
            return None
        return Subscription.query.filter_by(gocardless_subscription_id=subscription_id).first()
    return dict(get_subscription_from_gocardless_subscription_id=get_subscription_from_gocardless_subscription_id)

@admin.context_processor
def utility_get_transaction_fulfillment_state():
    """return fulfullment_state of transaction"""
    def get_transaction_fulfillment_state(external_id):
        transaction = Transaction.query.filter_by(external_id=external_id).first()
        if transaction:
            return transaction.fulfillment_state
        else:
            return None
    return dict(get_transaction_fulfillment_state=get_transaction_fulfillment_state)


def get_subscription_status(gocardless_subscription_id) -> str:
    status_on_error = "Unknown"
    payment_provider = PaymentProvider.query.first()
    try:
        client = gocardless_pro.Client(
            access_token = payment_provider.gocardless_access_token,
            environment= payment_provider.gocardless_environment
        )
    except ValueError as e:
        print(e)
        return "Unknown"

    try:
        response = client.subscriptions.get(gocardless_subscription_id)
        return response.status if hasattr(response, "status") else status_on_error
    except Exception as e:
        logging.error(e)
        return status_on_error


@admin.context_processor
def subscription_status():
    def formatted_status(gocardless_subscription_id):
        return get_subscription_status(gocardless_subscription_id).capitalize().replace("_", " ")
    return dict(subscription_status=formatted_status)


@admin.route("/subscribers")
@login_required
def subscribers():
    page = request.args.get('page', 1, type=int)

    people = database.session.query(Person).order_by(desc(Person.created_at)).paginate(page=page, per_page=5)

    return render_template(
            'admin/subscribers.html', people=people
            )

@admin.route("/upcoming-payments")
@login_required
def upcoming_payments():

    previous_page_cursor = request.args.get('previous', None)
    next_page_cursor = request.args.get('next', None)

    payment_provider = PaymentProvider.query.first()        
    client = gocardless_pro.Client(
        access_token=payment_provider.gocardless_access_token,
        environment=payment_provider.gocardless_environment,
    )

    # Get latest payments
    payments = client.payments.list(params={"limit":10}).records

    # Paginate
    try:
        latest_payment_id = payments[-1].id
        
        if next_page_cursor:
            payments = client.payments.list(params={"after": next_page_cursor,
                                                    "limit": 10}
                    ).records

        next_page_cursor = payments[-1].id

        previous_payments = client.payments.list(params={"before": next_page_cursor,
                                                    "limit": 10}
                ).records
        previous_page_cursor = previous_payments[-1].id
    except IndexError:
        payments = [] # No payments yet 

    # Store / Update transactions table
    for payment in payments:
        store_gocardless_transaction(payment.id)

    return render_template(
            'admin/upcoming_payments.html', payments=payments,
            datetime=datetime,
            next_page_cursor=next_page_cursor,
            previous_page_cursor=previous_page_cursor
            )

@admin.route("/customers", methods=["GET"])
@login_required
def customers():
    payment_provider = PaymentProvider.query.first()        
    from SSOT import SSOT
    
    target_gateways = ()

    if payment_provider.gocardless_active:
        access_token = payment_provider.gocardless_access_token,
        gc_environment = payment_provider.gocardless_environment,
        target_gateways = target_gateways + ({"name": "GoCardless", 
                                              "construct": {
                                                "access_token":access_token,
                                                "environment": gc_environment
                                                }
                                            },)

    if payment_provider.stripe_active:
        stripe_token = payment_provider.stripe_secret_key
        target_gateways = target_gateways + ({"name": "Stripe", "construct": stripe_token},)

    try:
        SSOT = SSOT(target_gateways)
        partners = SSOT.partners
    except gocardless_pro.errors.InvalidApiUsageError as e:
        logging.error(e.type)
        logging.error(e.message)
        flash("Invalid GoCardless API token. Correct your GoCardless API key.")
        return redirect(url_for("admin.connect_gocardless_manually"))
    except ValueError as e:
        logging.error(e.message)
        if e.message == "No access_token provided":
            flash("You must connect your GoCardless account first.")
            return redirect(url_for("admin.connect_gocardless_manually"))
        else:
            raise
    return render_template("admin/customers.html", partners=partners)


@admin.route("/transactions", methods=["GET"])
@login_required
def transactions():

    page = request.args.get('page', 1, type=int)
    transactions = database.session.query(Transaction).order_by(desc(Transaction.created_at)).paginate(page=page, per_page=10)
    
    return render_template(
        "admin/transactions.html", transactions=transactions
    )

@admin.route("/order-notes", methods=["GET"])
@login_required
def order_notes():
  """Notes to seller given during subscription creation"""
  subscriptions = Subscription.query.order_by(desc('created_at')).all()
  return render_template("admin/order-notes.html", 
                         subscriptions=subscriptions)

@admin.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
  """Change password of existing user"""
  form = ChangePasswordForm()
  if request.method == "POST":
      email = session.get('user_id', None)
      if email is None:
          return "Email not found in session"

      if form.validate_on_submit():
          user = User.query.filter_by(email=email).first()
          if user is None:
              return "User not found with that email"
          else:
              user.set_password(request.form["password"])
              database.session.commit()
          flash("Password has been updated")
      else:
          return "Invalid password form submission"
      return redirect(url_for('admin.change_password'))
  else:
      return render_template("admin/change_password.html", form=form)


@admin.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
  """Change email of existing user"""
  form = ChangeEmailForm()
  if request.method == "POST":
      email = session.get('user_id', None)
      if email is None:
          return "Email not found in session"

      if form.validate_on_submit():
          user = User.query.filter_by(email=email).first()
          if user is None:
              return "User not found with that email"
          else:
              new_email = request.form["email"]
              user.email = new_email
              database.session.commit()
          flash(f"Email has been updated to {new_email}. Please re-login")
      else:
          return "Invalid email form submission"
      return redirect(url_for('admin.change_email'))
  else:
      return render_template("admin/change_email.html", form=form)

@admin.route("/add-shop-admin", methods=["GET", "POST"])
@login_required
def add_shop_admin():
  """Add another shop admin"""
  form = AddShopAdminForm()
  if request.method == "POST":

      if form.validate_on_submit():
          # Check user dosent already exist
          email = request.form["email"]
          if User.query.filter_by(email=email).first() is not None:
              return f"Error, admin with email ({email}) already exists."

          user = User()
          user.email = email
          user.set_password(request.form["password"])
          database.session.add(user)
          database.session.commit()
          flash(f"A new shop admin with email {email} has been added")
      else:
          return "Invalid add shop admin form submission"
      return redirect(url_for('admin.add_shop_admin'))
  else:
      return render_template("admin/add_shop_admin.html", form=form)

@admin.route("/upload-logo", methods=["GET", "POST"])
@login_required
def upload_logo():
    """Upload shop logo"""
    form = UploadLogoForm()
    company = Company.query.first()

    if form.validate_on_submit():
        images = UploadSet("images", IMAGES)
        f = form.image.data
        if f is None:
            flash("File required")
        else:
            filename = images.save(f)
            # symlink to active theme static directory
            img_src = "".join(
                [current_app.config["UPLOADED_IMAGES_DEST"], filename]
            )
            link = "".join([current_app.config["STATIC_FOLDER"], filename])
            symlink(img_src, link, overwrite=True)
            src = url_for("static", filename=filename)
            company.logo_src = src
            database.session.commit()
            flash("Logo has been uploaded")

    return render_template("admin/upload_logo.html", form=form, company=company)

@admin.route("/remove-logo", methods=["GET"])
@login_required
def remove_logo():
    """Remove logo from shop"""
    company = Company.query.first()
    company.logo_src = None
    database.session.commit()
    flash("Logo removed")
    # Return user to previous page
    return redirect(request.referrer)


@admin.route("/welcome-email-edit", methods=["GET", "POST"])
@login_required
def edit_welcome_email():
    """Edit welcome email template"""
    company = Company.query.first()
    form = WelcomeEmailTemplateForm()
    default_template = open(Path(current_app.root_path + '/emails/welcome.jinja2.html')).read()
    custom_template = EmailTemplate.query.first()

    if custom_template is None: # First time creating custom template
        custom_template = EmailTemplate()
        database.session.add(custom_template)

    if form.validate_on_submit() and form.use_custom_welcome_email.data is True:

        new_custom_template = form.template.data
        # Validate template syntax
        env = Environment()
        try:
            env.parse(new_custom_template)
            # Store the validated template
            custom_template.custom_welcome_email_template = new_custom_template
            custom_template.use_custom_welcome_email = True
            flash("Email template has been saved.")
            flash("Using custom template for welcome email")
        except jinja2.exceptions.TemplateSyntaxError as e:
            form.template.errors.append(e)

    else:
        custom_template.use_custom_welcome_email = False
        if request.method == "POST":
            flash("Using default template for welcome email")

    database.session.commit()

    return render_template("admin/email/edit_customer_sign_up_email.html", form=form, 
                          default_template=default_template,
                          custom_template=custom_template.custom_welcome_email_template,
                          use_custom_welcome_email=custom_template.use_custom_welcome_email,
                          company=company)

@admin.route("/set-reply-to-email", methods=["GET", "POST"])
@login_required
def set_reply_to_email():
    """Set reply-to email"""
    form = SetReplyToEmailForm()
    setting = Setting.query.first()
    if setting is None:
        setting = Setting()
        database.session.add(setting)

    current_email = setting.reply_to_email_address

    if form.validate_on_submit():
        email = form.email.data
        setting.reply_to_email_address = email
        database.session.commit()
        flash(f"Reply-to email address set to: {email}")
    return render_template("admin/settings/set_reply_to_email.html", form=form,
                          current_email=current_email)

@admin.route("/upload-files", methods=["GET", "POST"])
@login_required
def upload_files():
    """Upload files to shop"""
    form = UploadFilesForm()
    allowed= ["image/png", "image/gif", "image/jpg", "image/jpeg", 
             "audio/mpeg", "video/mpeg", "audio/ogg", "video/ogg", 
             "application/ogg", "application/pdf", "application/vnd.ms-powerpoint",
             "application/vnd.ms-excel", "application/msword", 
             "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
             "application/vnd.openxmlformats-officedocument.presentationml.presentation"]
    if form.validate_on_submit():
        for upload in request.files.getlist('upload'):
            # Check filetype
            if upload.content_type in allowed:
                filename = secure_filename(upload.filename)
                # Store to filesystem
                upload.save(dst=current_app.config["UPLOADED_FILES_DEST"] + "/" + filename)
                # Store file meta in db
                uploadedFile = File()
                uploadedFile.file_name = filename
                database.session.add(uploadedFile)
                flash(f"Uploaded {filename}")
        database.session.commit()
    return render_template("admin/uploads/upload_files.html", form=form)


@admin.route("/list-files", methods=["GET"])
@login_required
def list_files():
    files = File.query.all()
    return render_template("admin/uploads/list_files.html", files=files)

@admin.route('/delete/file/<uuid>')
@login_required
def delete_file(uuid):
    # Remove from database file meta
    theFile = File.query.filter_by(uuid=uuid).first()
    if theFile is not None:
        database.session.delete(theFile)

    database.session.commit()
    # Remove from filesystem
    try:
        os.unlink(current_app.config['UPLOADED_FILES_DEST'] + theFile.file_name)
    except Exception as e:
        print(e)
    flash(f"Deleted: {theFile.file_name}")
    return redirect(request.referrer)

@admin.route('/uploads/<uuid>')
@protected_download
def download_file(uuid):
    theFile = File.query.filter_by(uuid=uuid).first()
    if theFile is not None:
        return send_from_directory(current_app.config['UPLOADED_FILES_DEST'],
                                   theFile.file_name, as_attachment=True)
    else:
        return "Not found", 404

def getPlan(container, i, default=None):
    try:
        return container[i]
    except IndexError:
        return default
