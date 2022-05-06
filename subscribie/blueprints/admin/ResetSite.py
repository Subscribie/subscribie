import os
from . import admin
from subscribie.auth import login_required
from subscribie.database import database
from subscribie.models import (
    Subscription,
    Person,
    Transaction,
    PaymentProvider,
    TaxRate,
)
from flask import jsonify
from subscribie.utils import get_stripe_connect_account_id, get_stripe_secret_key
import stripe


@admin.route("/remove-subscriptions", methods=["GET"])
@login_required
def remove_subscriptions():
    if os.getenv("FLASK_ENV") != "development":
        msg = {"msg": "Error. Only possible in development mode"}
        return jsonify(msg), 403
    database.session.query(Subscription).delete()
    database.session.commit()

    msg = {"msg": "all subscriptions deleted"}

    return jsonify(msg)


@admin.route("/remove-people", methods=["GET"])
@login_required
def remove_people():
    if os.getenv("FLASK_ENV") != "development":
        msg = {"msg": "Error. Only possible in development mode"}
        return jsonify(msg), 403
    database.session.query(Person).delete()
    database.session.commit()

    msg = {"msg": "all people deleted"}

    return jsonify(msg)


@admin.route("/remove-transactions", methods=["GET"])
@login_required
def remove_transactions():
    if os.getenv("FLASK_ENV") != "development":
        msg = {"msg": "Error. Only possible in development mode"}
        return jsonify(msg), 403
    database.session.query(Transaction).delete()
    database.session.commit()

    msg = {"msg": "all transactions deleted"}

    return jsonify(msg)


@admin.route("/delete-connect-account", methods=["GET"])
@login_required
def delete_connect_account():
    if os.getenv("FLASK_ENV") != "development":
        msg = {"msg": "Error. Only possible in development mode"}
        return jsonify(msg), 403
    stripe.api_key = get_stripe_secret_key()
    connect_account_id = get_stripe_connect_account_id()
    if connect_account_id:
        stripe.Account.delete(get_stripe_connect_account_id())
        database.session.query(PaymentProvider).delete()
        database.session.query(TaxRate).delete()
        database.session.commit()
        msg = {"msg": "stripe connect accound id deleted"}
        return jsonify(msg)
    else:

        msg = {"msg": "please connect to stripe"}

        return jsonify(msg)
