from flask import Blueprint, render_template, abort, flash, json
from jinja2 import TemplateNotFound, Markup
from subscribie import (
    logging,
    Jamla,
    session,
    render_template,
    request,
    redirect,
    gocardless_pro,
    GocardlessConnectForm,
    StripeConnectForm,
    current_app,
    redirect,
    url_for,
    GoogleTagManagerConnectForm,
    ItemsForm,
    jsonify,
    TawkConnectForm,
    database, User, Person, Subscription, SubscriptionNote
)
from subscribie.auth import login_required
from subscribie.db import get_jamla, get_db
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

admin_theme = Blueprint(
    "admin", __name__, template_folder="templates", static_folder="static"
)

@admin_theme.app_template_filter()
def currencyFormat(value):
  value = float(value)/100
  return "£{:,.2f}".format(value)

@admin_theme.route("/gocardless/subscriptions/<subscription_id>/actions/pause")
@login_required
def pause_gocardless_subscription(subscription_id):
    """Pause a GoCardless subscription"""
    jamla = get_jamla()
    gocclient = gocardless_pro.Client(
      access_token=jamla["payment_providers"]["gocardless"]["access_token"],
          environment=jamla["payment_providers"]["gocardless"]["environment"],
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
    jamla = get_jamla()
    gocclient = gocardless_pro.Client(
      access_token=jamla["payment_providers"]["gocardless"]["access_token"],
          environment=jamla["payment_providers"]["gocardless"]["environment"],
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
  jamla = get_jamla()
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
      gocclient = gocardless_pro.Client(
          access_token=jamla["payment_providers"]["gocardless"]["access_token"],
          environment=jamla["payment_providers"]["gocardless"]["environment"],
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
  return render_template("admin/cancel_mandates_confirm.html", email=email,
                        jamla=jamla)

@admin_theme.route("/dashboard")
@login_required
def dashboard():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
        
    if jamlaApp.has_connected("gocardless"):
        gocardless_connected = True
    else:
        gocardless_connected = False
    if jamlaApp.has_connected("stripe"):
        stripe_connected = True
    else:
        stripe_connected = False
    return render_template(
        "admin/dashboard.html",
        jamla=jamla,
        gocardless_connected=gocardless_connected,
        stripe_connected=stripe_connected,
        loadedModules=getLoadedModules()
    )


@admin_theme.route("/edit", methods=["GET", "POST"])
@login_required
def edit_jamla():
    """Update jamla items
    
    Note sku items are immutable, when a change is made to an item, its old
    item is archived and a new sku item is created with a new uuid. This is to
    protect data integriry and make sure plan history is retained, via its uuid.
    If a user needs to change a subscription, they should change to a different
    plan with a different uuid.

    """

    form = ItemsForm()
    jamla = get_jamla()
    # Filter archived items                                                      
    jamlaApp = Jamla()
    jamla = jamlaApp.filter_archived_items(jamla)
    if form.validate_on_submit():
        jamla["company"]["name"] = request.form["company_name"]
        jamla["company"]["slogan"] = request.form["slogan"]
        jamla["users"][0] = request.form["email"]
        # Loop items
        for index in request.form.getlist("itemIndex", type=int):

            # Archive existing item then create new sku item
            # (remember, edit edits create new items because
            # skus are immutable)

            jamla["items"][index]["archived"] = True # Archive item

            # Build new sku
            draftItem = {}
            draftItem["uuid"] = str(uuid.uuid4())
            draftItem["requirements"] = {}
            # Preserve primary icon if exists
            draftItem["primary_icon"] = jamla["items"][index]["primary_icon"]

            draftItem["title"] = getItem(
                form.title.data, index, default=""
            ).strip()

            draftItem["sku"] = draftItem["title"].replace(" ", "").strip()

            draftItem["requirements"]["subscription"] = bool(
                getItem(form.subscription.data, index)
            )
            if getItem(form.monthly_price.data, index, default=0) is None:
                monthly_price = 0
            else:
                monthly_price = int(getItem(form.monthly_price.data, index, default=0) * 100)
            draftItem["monthly_price"] = monthly_price

            draftItem["requirements"]["instant_payment"] = bool(
                getItem(form.instant_payment.data, index)
            )
            draftItem["requirements"]["note_to_seller_required"] = bool(
                getItem(form.note_to_seller_required.data, index)
            )

            draftItem["requirements"]["note_to_buyer_message"] = str(getItem(
                form.note_to_buyer_message, index, default=""
            ).data)

            try:
                days_before_first_charge = int(form.days_before_first_charge[index].data)
            except ValueError:
                days_before_first_charge = 0

            draftItem["days_before_first_charge"] = days_before_first_charge

            if getItem(form.sell_price.data, index, default=0) is None:
                sell_price = 0
            else:
                sell_price = int(getItem(form.sell_price.data, index, default=0) * 100)
            draftItem["sell_price"] = sell_price

            draftItem["selling_points"] = getItem(
                form.selling_points.data, index, default=""
            )
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
                draftItem["primary_icon"] = {"src": src, "type": ""}
            # Add new sku to items
            jamla["items"].append(draftItem)
            fp = open(current_app.config["JAMLA_PATH"], "w")
            yaml.safe_dump(jamla, fp, default_flow_style=False)
        flash("Item(s) updated.")
        # Trigger a reload by touching the wsgi file.
        # Which file we need to touch depends on the wsgi config
        # e.g. on uwsgi to set it to subscribie.wsgi on uwsgi we pass:
        # uwsgi --http :9090 --workers 2 --wsgi-file subscribie.wsgi \
        #  --touch-chain-reload subscribie.wsgi
        # To uwsgi. The `--touch-chain-reload` option tells uwsgi to perform
        # a graceful reload. "When triggered, it will restart one worker at 
        # time, and the following worker is not reloaded until the previous one
        # is ready to accept new requests. We must use more than one worker for
        # this to work. See:
        # https://uwsgi-docs.readthedocs.io/en/latest/articles/TheArtOfGracefulReloading.html#chain-reloading-lazy-apps
        wsgiFile = os.path.abspath(''.join([os.getcwd(), '/subscribie.wsgi']))
        p = Path(wsgiFile)
        p.touch(exist_ok=True) # Triggers the graceful reload
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/edit_jamla.html", jamla=jamla, form=form)


#    return render_template('formarraybasic/index.html')


@admin_theme.route("/add", methods=["GET", "POST"])
@login_required
def add_jamla_item():
    form = ItemsForm()
    jamla = get_jamla()
    if form.validate_on_submit():
        draftItem = {}
        draftItem["uuid"] = str(uuid.uuid4())
        draftItem["requirements"] = {}
        draftItem["primary_icon"] = {"src": "", "type": ""}
        draftItem["title"] = form.title.data[0].strip()
        draftItem["requirements"]["subscription"] = bool(form.subscription.data[0])
        draftItem["requirements"]["note_to_seller_required"] = bool(form.note_to_seller_required.data[0])
        draftItem["requirements"]["note_to_buyer_message"] = str(form.note_to_buyer_message.data[0])
        try:
            days_before_first_charge = int(form.days_before_first_charge.data[0])
        except ValueError:
            days_before_first_charge = 0

        draftItem["days_before_first_charge"] = days_before_first_charge

        if form.monthly_price.data[0] is None:
            draftItem["monthly_price"] = False
        else:
            draftItem["monthly_price"] = int(form.monthly_price.data[0]) * 100
        draftItem["requirements"]["instant_payment"] = bool(
            form.instant_payment.data[0]
        )
        if form.sell_price.data[0] is None:
            draftItem["sell_price"] = False
        else:
            draftItem["sell_price"] = int(form.sell_price.data[0]) * 100
        draftItem["selling_points"] = form.selling_points.data[0]
        # Create SKU
        draftItem["sku"] = form.title.data[0].replace(" ", "").strip()
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
            draftItem["primary_icon"] = {"src": src, "type": ""}
        jamla["items"].append(draftItem)
        fp = open(current_app.config["JAMLA_PATH"], "w")
        yaml.safe_dump(jamla, fp, default_flow_style=False)
        flash("Item added.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/add_jamla_item.html", jamla=jamla, form=form)


@admin_theme.route("/delete", methods=["GET"])
@login_required
def delete_jamla_item():
    jamla = get_jamla()
    # Filter archived items                                                      
    jamlaApp = Jamla()
    jamla = jamlaApp.filter_archived_items(jamla)
    return render_template("admin/delete_jamla_item_choose.html", jamla=jamla)


@admin_theme.route("/delete/<sku>", methods=["GET", "POST"])
@login_required
def delete_item_by_sku(sku):
    """Archive (dont actually delete) an item"""
    jamla = get_jamla()
    # Filter archived items                                                      
    jamlaApp = Jamla()
    jamla = jamlaApp.filter_archived_items(jamla)

    jamlaApp = Jamla()
    jamlaApp.load(jamla=get_jamla())
    itemIndex = jamlaApp.sku_get_index(sku)
    if "confirm" in request.args:
        confirm = False
        return render_template(
            "admin/delete_jamla_item_choose.html",
            jamla=jamla,
            itemSKU=sku,
            confirm=False,
        )
    if itemIndex is not False:
        # Perform removal
        jamla["items"][itemIndex]['archived'] = True
        fp = open(current_app.config["JAMLA_PATH"], "w")
        yaml.safe_dump(jamla, fp, default_flow_style=False)

    flash("Item deleted.")
    return render_template("admin/delete_jamla_item_choose.html", jamla=jamla)


@admin_theme.route("/connect/gocardless/manually", methods=["GET", "POST"])
@login_required
def connect_gocardless_manually():
    form = GocardlessConnectForm()
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if jamlaApp.has_connected("gocardless"):
        gocardless_connected = True
    else:
        gocardless_connected = False
    if form.validate_on_submit():
        access_token = form.data["access_token"]
        jamla["payment_providers"]["gocardless"]["access_token"] = access_token
        # Check if live or test api key was given
        if "live" in access_token:
            jamla["payment_providers"]["gocardless"]["environment"] = "live"
        else:
            jamla["payment_providers"]["gocardless"]["environment"] = "sandbox"

        fp = open(current_app.config["JAMLA_PATH"], "w")
        # Overwrite jamla file with gocardless access_token
        yaml.safe_dump(jamla, fp, default_flow_style=False)
        # Set users current session to store access_token for instant access
        session["gocardless_access_token"] = access_token
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_gocardless_manually.html",
            form=form,
            jamla=jamla,
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


@admin_theme.route("/connect/gocardless/oauth/complete", methods=["GET"])
@login_required
def gocardless_oauth_complete():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    flow = OAuth2WebServerFlow(
        client_id=current_app.config["GOCARDLESS_CLIENT_ID"],
        client_secret=current_app.config["GOCARDLESS_CLIENT_SECRET"],
        scope="read_write",
        # You'll need to use exactly the same redirect URI as in the last
        # step
        redirect_uri="http://127.0.0.1:5000/connect/gocardless/oauth/complete",
        auth_uri="https://connect-sandbox.gocardless.com/oauth/authorize",
        token_uri="https://connect-sandbox.gocardless.com/oauth/access_token",
        initial_view="signup",
    )
    access_token = flow.step2_exchange(request.args.get("code"))

    jamla["payment_providers"]["gocardless"]["access_token"] = access_token.access_token
    fp = open(current_app.config["JAMLA_PATH"], "w")
    # Overwrite jamla file with gocardless access_token
    yaml.safe_dump(jamla, fp, default_flow_style=False)
    # Set users current session to store access_token for instant access
    session["gocardless_access_token"] = access_token.access_token
    session["gocardless_organisation_id"] = access_token.token_response[
        "organisation_id"
    ]

    return redirect(url_for("admin.dashboard"))


@admin_theme.route("/connect/stripe/manually", methods=["GET", "POST"])
@login_required
def connect_stripe_manually():
    form = StripeConnectForm()
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if jamlaApp.has_connected("stripe"):
        stripe_connected = True
    else:
        stripe_connected = False
    if form.validate_on_submit():
        publishable_key = form.data["publishable_key"].strip()
        secret_key = form.data["secret_key"].strip()
        jamla["payment_providers"]["stripe"]["publishable_key"] = publishable_key
        jamla["payment_providers"]["stripe"]["secret_key"] = secret_key
        # Overwrite jamla file with gocardless access_token
        fp = open(current_app.config["JAMLA_PATH"], "w")
        yaml.safe_dump(jamla, fp, default_flow_style=False)
        session["stripe_publishable_key"] = publishable_key
        # Set stripe public key JS
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_stripe_manually.html",
            form=form,
            jamla=jamla,
            stripe_connected=stripe_connected,
        )


@admin_theme.route("/connect/google_tag_manager/manually", methods=["GET", "POST"])
@login_required
def connect_google_tag_manager_manually():
    form = GoogleTagManagerConnectForm()
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if form.validate_on_submit():
        container_id = form.data["container_id"]
        jamla["integrations"]["google_tag_manager"]["container_id"] = container_id
        jamla["integrations"]["google_tag_manager"]["active"] = True
        # Overwrite jamla file with google tag manager container_id
        fp = open(current_app.config["JAMLA_PATH"], "w")
        yaml.safe_dump(jamla, fp, default_flow_style=False)
        session["google_tag_manager_container_id"] = container_id
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "connect_google_tag_manager_manually.html", form=form, jamla=jamla
        )


@admin_theme.route("/connect/tawk/manually", methods=["GET", "POST"])
@login_required
def connect_tawk_manually():
    form = TawkConnectForm()
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if form.validate_on_submit():
        property_id = form.data["property_id"]
        jamla["integrations"]["tawk"]["property_id"] = property_id
        jamla["integrations"]["tawk"]["active"] = True
        # Overwrite jamla file with google tag manager container_id
        fp = open(current_app.config["JAMLA_PATH"], "w")
        yaml.safe_dump(jamla, fp, default_flow_style=False)
        session["tawk_property_id"] = property_id
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_tawk_manually.html", form=form, jamla=jamla
        )


@admin_theme.route("/jamla", methods=["GET"])
@admin_theme.route("/api/jamla", methods=["GET"])
@login_required
def fetch_jamla():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    # Strip out private values TODO don't store them here, move to .env?
    jamla["payment_providers"] = None
    resp = dict(
        items=jamla["items"],
        company=jamla["company"],
        name="fred",
        email="me@example.com",
    )
    return jsonify(resp)


@admin_theme.route("/push-payments", methods=["GET"])
def push_payments():
    """                                                                          
    Push payments to Penguin.                                                    
    Assume a gocardless endpoint for now.                                        
    """
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    gocclient = gocardless_pro.Client(
        access_token=get_secret("gocardless", "access_token"),
        environment=jamla["payment_providers"]["gocardless"]["environment"],
    )
    # Loop customers
    for payments in gocclient.payments.list().records:
        ##Loop each payment within payment response body
        response = payments.api_response.body
        for payment in response["payments"]:
            logging.info(payment)
            logging.info("The payment status is: %s", payment["status"])
            logging.info("Creating transaction to penguin")
            title = "a transaction title"
            try:
                payout_id = payment["links"]["payout"]
            except:
                payout_id = None
            fields = {
                "title": title,
                "field_gocardless_payment_id": payment["id"],
                "field_gocardless_payout_id": payout_id,
                "field_gocardless_amount": payment["amount"],
                "field_gocardless_payment_status": payment["status"],
                "field_mandate_id": payment["links"]["mandate"],
                "field_gocardless_subscription_id": payment["links"]["subscription"],
                "field_gocardless_amount_refunded": payment["amount_refunded"],
                "field_gocardless_charge_date": payment["charge_date"],
                "field_gocardless_created_at": payment["created_at"],
                "field_gocardless_creditor_id": payment["links"]["creditor"],
            }
            Rest.post(entity="transaction", fields=fields)

    return "Payments have been pushed"


@admin_theme.route("/retry-payment/<payment_id>", methods=["GET"])
def retry_payment(payment_id):
    jamla = get_jamla()
    jamlaapp = jamla()
    jamlaapp.load(jamla=jamla)
    gocclient = gocardless_pro.Client(
        access_token=get_secret("gocardless", "access_token"),
        environment=jamla["payment_providers"]["gocardless"]["environment"],
    )
    r = gocclient.payments.retry(payment_id)

    return "Payment (" + payment_id + " retried." + str(r)


@admin_theme.route("/ssot/refresh/<resource>", methods=["GET"])
@login_required
def refresh_ssot(resource):
  """Refresh SSOT to fetch newest customers (aka partners) and transactions
  resource is either "customers" or "transactions"
  """
  jamla = get_jamla()
  from SSOT import SSOT

  access_token = jamla["payment_providers"]["gocardless"]["access_token"]
  gc_environment = jamla["payment_providers"]["gocardless"]["environment"]
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
  jamla = get_jamla()
  from SSOT import SSOT

  access_token = jamla["payment_providers"]["gocardless"]["access_token"]
  gc_environment = jamla["payment_providers"]["gocardless"]["environment"]
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


def get_subscription_status(gocardless_subscription_id) -> str:
    status_on_error = "Unknown"

    jamla = get_jamla()
    client = gocardless_pro.Client(
        access_token=jamla["payment_providers"]["gocardless"]["access_token"],
        environment=jamla["payment_providers"]["gocardless"]["environment"],
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


@admin_theme.context_processor
def utility_jamla():
    def show(sku_uuid):
        jamla = get_jamla()
        jamlaApp = Jamla()
        jamlaApp.load(jamla=jamla)
        try:
            item = jamlaApp.sku_get_by_uuid(sku_uuid)
        except Exception:
            return None
        return item
    return dict(jamla_get=show)

@admin_theme.route("/subscribers")
@login_required
def subscribers():
    page = request.args.get('page', 1, type=int)

    people = database.session.query(Person).order_by(desc(Person.created_at)).paginate(page=page, per_page=5)
    jamla = get_jamla()

    return render_template(
            'admin/subscribers.html', people=people,
            jamla=jamla
            )

@admin_theme.route("/upcoming-payments")
@login_required
def upcoming_payments():
    jamla = get_jamla()
    client = gocardless_pro.Client(
        access_token=jamla["payment_providers"]["gocardless"]["access_token"],
        environment=jamla["payment_providers"]["gocardless"]["environment"],
    )

    payments = client.payments.list().records

    return render_template(
            'admin/upcoming_payments.html', payments=payments,
            jamla=jamla,
            datetime=datetime
            )

@admin_theme.route("/customers", methods=["GET"])
@login_required
def customers():
    jamla = get_jamla()
    from SSOT import SSOT
    
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)

    target_gateways = ()

    if jamlaApp.has_connected("gocardless"):
        access_token = jamla["payment_providers"]["gocardless"]["access_token"]
        gc_environment = jamla["payment_providers"]["gocardless"]["environment"]
        target_gateways = target_gateways + ({"name": "GoCardless", 
                                              "construct": {
                                                "access_token":access_token,
                                                "environment": gc_environment
                                                }
                                            },)

    if jamlaApp.has_connected("stripe"):
        stripe_token = jamla["payment_providers"]["stripe"]["secret_key"]
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
    return render_template("admin/customers.html", jamla=jamla, partners=partners)


@admin_theme.route("/transactions", methods=["GET"])
@login_required
def transactions():
    jamla = get_jamla()
    from SSOT import SSOT

    access_token = jamla["payment_providers"]["gocardless"]["access_token"]
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
        "admin/transactions.html", jamla=jamla, transactions=transactions
    )
@admin_theme.route("/order-notes", methods=["GET"])
@login_required
def order_notes():
  """Notes to seller given during subscription creation"""
  subscriptions = Subscription.query.order_by(desc('created_at')).all()
  jamla = get_jamla()
  return render_template("admin/order-notes.html", jamla=jamla, 
                         subscriptions=subscriptions)


def getItem(container, i, default=None):
    try:
        return container[i]
    except IndexError:
        return default
