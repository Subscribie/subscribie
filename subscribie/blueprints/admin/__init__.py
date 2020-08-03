from flask import Blueprint, render_template, abort, flash, json
from jinja2 import TemplateNotFound, Markup
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
    ItemsForm,
    jsonify,
    TawkConnectForm,
    database, User, Person, Subscription, SubscriptionNote, Company,
    Integration, PaymentProvider, Plan, PlanRequirements, PlanSellingPoints
)
from subscribie.auth import login_required
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
from subscribie.models import Transaction

admin_theme = Blueprint(
    "admin", __name__, template_folder="templates", static_folder="static"
)

@admin_theme.app_template_filter()
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


@admin_theme.route("payments/update/<gocardless_payment_id>")
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

@admin_theme.route("/gocardless/subscriptions/<subscription_id>/actions/pause")
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

@admin_theme.route("/gocardless/subscriptions/<subscription_id>/actions/resume")
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

@admin_theme.route("/cancel/mandates/<email>")
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

@admin_theme.route("/dashboard")
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


@admin_theme.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit items
    
    Note items are immutable, when a change is made to an item, its old
    item is archived and a new item is created with a new uuid. This is to
    protect data integriry and make sure plan history is retained, via its uuid.
    If a user needs to change a subscription, they should change to a different
    plan with a different uuid.

    """

    form = ItemsForm()
    items = Item.query.filter_by(archived=0).all()
    if form.validate_on_submit():
        company = Company.query.first()
        company.name  = request.form["company_name"]
        company.slogan = request.form["slogan"]
        # Loop items
        for index in request.form.getlist("itemIndex", type=int):

            # Archive existing item then create new item
            # (remember, edits create new items because
            # items are immutable)
            item = Item.query.filter_by(uuid=form.uuid.data[index]).first()
            item.archived = True

            # Build new item
            draftItem = Item()
            database.session.add(draftItem)
            item_requirements = ItemRequirements()

            draftItem.uuid = str(uuid.uuid4())
            draftItem.requirements = item_requirements
            # Preserve primary icon if exists
            draftItem.primary_icon = item.primary_icon

            draftItem.title = getItem(
                form.title.data, index, default=""
            ).strip()

            if getItem(form.subscription.data, index) == 'yes':
                item_requirements.subscription = True
            else:
                item_requirements.subscription = False

            interval_unit = getItem(
                    form.interval_unit.data, index, default=""
            )
            if 'monthly' in interval_unit or 'yearly' in interval_unit or \
               'weekly' in interval_unit:
                   draftItem.interval_unit = interval_unit

            if getItem(form.interval_amount.data, index, default=0) is None:
                interval_amount = 0
            else:
                interval_amount = int(getItem(form.interval_amount.data, index, default=0) * 100)
            draftItem.interval_amount = interval_amount
            if getItem(form.instant_payment.data, index) == 'yes':
                item_requirements.instant_payment = True
            else:
                item_requirements.instant_payment = False

            if getItem(form.note_to_seller_required.data, index) == 'yes':
                item_requirements.note_to_seller_required = True
            else:
                item_requirements.note_to_seller_required = False

            item_requirements.note_to_buyer_message = str(getItem(
                form.note_to_buyer_message, index, default=""
            ).data)

            try:
                days_before_first_charge = int(form.days_before_first_charge[index].data)
            except ValueError:
                days_before_first_charge = 0

            draftItem.days_before_first_charge = days_before_first_charge

            if getItem(form.sell_price.data, index, default=0) is None:
                sell_price = 0
            else:
                sell_price = int(getItem(form.sell_price.data, index, default=0) * 100)

            draftItem.sell_price = sell_price

            points = getItem(
                form.selling_points.data, index, default=""
            )
            for point in points:
                draftItem.selling_points.append(ItemSellingPoints(point=point))

            # Primary icon image storage
            f = getItem(form.image.data, index)
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
                draftItem.primary_icon = src
        database.session.commit() # Save
        flash("Item(s) updated.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit.html", items=items, form=form)



@admin_theme.route("/add", methods=["GET", "POST"])
@login_required
def add_item():
    form = ItemsForm()
    if form.validate_on_submit():
        draftItem = Item()
        database.session.add(draftItem)
        item_requirements = ItemRequirements()
        draftItem.requirements = item_requirements

        draftItem.uuid = str(uuid.uuid4())
        draftItem.title = form.title.data[0].strip()
        interval_unit = form.interval_unit.data[0].strip()
        if 'monthly' in interval_unit or 'yearly' in interval_unit or \
           'weekly' in interval_unit:
               draftItem.interval_unit = interval_unit

        if form.subscription.data[0] == 'yes':
            item_requirements.subscription = True
        else:
            item_requirements.subscription = False
        if form.note_to_seller_required.data[0] == 'yes':
            item_requirements.note_to_seller_required = True
        else:
            item_requirements.note_to_seller_required = False

        item_requirements.note_to_buyer_message = str(form.note_to_buyer_message.data[0])
        try:
            days_before_first_charge = int(form.days_before_first_charge.data[0])
        except ValueError:
            days_before_first_charge = 0

        draftItem.days_before_first_charge = days_before_first_charge

        if form.interval_amount.data[0] is None:
            draftItem.interval_amount = 0
        else:
            draftItem.interval_amount = int(form.interval_amount.data[0]) * 100

        if form.instant_payment.data[0] == 'yes':
            item_requirements.instant_payment = True
        else:
            item_requirements.instant_payment = False

        if form.sell_price.data[0] is None:
            draftItem.sell_price = 0
        else:
            draftItem.sell_price = int(form.sell_price.data[0]) * 100

        points = form.selling_points.data[0]

        for point in points:
            draftItem.selling_points.append(ItemSellingPoints(point=point))

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
            draftItem.primary_icon = src
        database.session.commit()
        flash("Item added.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/add_item.html", form=form)


@admin_theme.route("/delete", methods=["GET"])
@login_required
def delete_item():
    items = Item.query.filter_by(archived=0).all()
    return render_template("admin/delete_item_choose.html", items=items)


@admin_theme.route("/delete/<uuid>", methods=["GET", "POST"])
@login_required
def delete_item_by_uuid(uuid):
    """Archive (dont actually delete) an item"""
    item = Item.query.filter_by(uuid=uuid).first()

    if "confirm" in request.args:
        confirm = False
        return render_template(
            "admin/delete_item_choose.html",
            confirm=False,
            item=item
        )
    if uuid is not False:
        # Perform archive
        item.archived = True
        database.session.commit()

    flash("Item deleted.")
    items = Item.query.filter_by(archived=0).all()
    return render_template("admin/delete_item_choose.html", items=items)


@admin_theme.route("/connect/gocardless/manually", methods=["GET", "POST"])
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


@admin_theme.route("/connect/gocardless", methods=["GET"])
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


@admin_theme.route("/connect/stripe/manually", methods=["GET", "POST"])
@login_required
def connect_stripe_manually():
    form = StripeConnectForm()
    payment_provider = PaymentProvider.query.first()        

    if payment_provider.stripe_active:
        stripe_connected = True
    else:
        stripe_connected = False
    if form.validate_on_submit():
        publishable_key = form.data["publishable_key"].strip()
        secret_key = form.data["secret_key"].strip()
        payment_provider.stripe_publishable_key = publishable_key
        payment_provider.stripe_secret_key = secret_key
        payment_provider.stripe_active = True
        database.session.commit() # Save changes
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_stripe_manually.html",
            form=form,
            stripe_connected=stripe_connected,
        )


@admin_theme.route("/connect/google_tag_manager/manually", methods=["GET", "POST"])
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


@admin_theme.route("/connect/tawk/manually", methods=["GET", "POST"])
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


@admin_theme.route("/retry-payment/<payment_id>", methods=["GET"])
def retry_payment(payment_id):
    payment_provider = PaymentProvider.query.first()        
    gocclient = gocardless_pro.Client(
      access_token=payment_provider.gocardless_access_token,
          environment=payment_provider.gocardless_environment,
    )
    r = gocclient.payments.retry(payment_id)

    return "Payment (" + payment_id + " retried." + str(r)


@admin_theme.route("/ssot/refresh/<resource>", methods=["GET"])
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
  

@admin_theme.context_processor
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

@admin_theme.context_processor
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

@admin_theme.context_processor
def utility_get_subscription_from_gocardless_subscription_id():
    """Return sqlalchemy Subscription object"""
    def get_subscription_from_gocardless_subscription_id(subscription_id):
        if subscription_id is None:
            return None
        return Subscription.query.filter_by(gocardless_subscription_id=subscription_id).first()
    return dict(get_subscription_from_gocardless_subscription_id=get_subscription_from_gocardless_subscription_id)

@admin_theme.context_processor
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
    client = gocardless_pro.Client(
        access_token = payment_provider.gocardless_access_token,
        environment= payment_provider.gocardless_environment
    )

    try:
        response = client.subscriptions.get(gocardless_subscription_id)
        return response.status if hasattr(response, "status") else status_on_error
    except Exception as e:
        logging.error(e)
        return status_on_error


@admin_theme.context_processor
def subscription_status():
    def formatted_status(gocardless_subscription_id):
        return get_subscription_status(gocardless_subscription_id).capitalize().replace("_", " ")
    return dict(subscription_status=formatted_status)


@admin_theme.route("/subscribers")
@login_required
def subscribers():
    page = request.args.get('page', 1, type=int)

    people = database.session.query(Person).order_by(desc(Person.created_at)).paginate(page=page, per_page=5)

    return render_template(
            'admin/subscribers.html', people=people
            )

@admin_theme.route("/upcoming-payments")
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

@admin_theme.route("/customers", methods=["GET"])
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


@admin_theme.route("/transactions", methods=["GET"])
@login_required
def transactions():
    payment_provider = PaymentProvider.query.first()        
    from SSOT import SSOT

    access_token = payment_provider.gocardless_access_token,
    target_gateways = ({"name": "GoCardless", "construct": access_token},)
    try:
        SSOT = SSOT(target_gateways)
        transactions = SSOT.transactions
    except gocardless_pro.errors.InvalidApiUsageError as e:
        logging.error(e.type)
        logging(e.message)
        flash("Invalid GoCardless API token. Correct your GoCardless API key.")
        return redirect(url_for("admin.connect_gocardless_manually"))
    except ValueError as e:
        logging.error(e.message)
        if e.message == "No access_token provided":
            flash("You must connect your GoCardless account first.")
            return redirect(url_for("admin.connect_gocardless_manually"))
        else:
            raise
    return render_template(
        "admin/transactions.html", transactions=transactions
    )
@admin_theme.route("/order-notes", methods=["GET"])
@login_required
def order_notes():
  """Notes to seller given during subscription creation"""
  subscriptions = Subscription.query.order_by(desc('created_at')).all()
  return render_template("admin/order-notes.html", 
                         subscriptions=subscriptions)

@admin_theme.route("/change-password", methods=["GET", "POST"])
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


@admin_theme.route("/change-email", methods=["GET", "POST"])
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

@admin_theme.route("/add-shop-admin", methods=["GET", "POST"])
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


def getItem(container, i, default=None):
    try:
        return container[i]
    except IndexError:
        return default
