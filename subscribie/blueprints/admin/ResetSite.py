from . import admin
from subscribie.auth import login_required, development_mode_only
from subscribie.database import database
from subscribie.models import (
    Subscription,
    Person,
    Transaction,
    PaymentProvider,
    TaxRate,
    Document,
)
from flask import jsonify
from subscribie.utils import get_stripe_connect_account_id, get_stripe_secret_key
import stripe


@admin.route("/remove-subscriptions", methods=["GET"])
@login_required
@development_mode_only
def remove_subscriptions():
    database.session.query(Subscription).delete()
    database.session.commit()

    msg = {"msg": "all subscriptions deleted"}

    return jsonify(msg)


@admin.route("/remove-people", methods=["GET"])
@login_required
@development_mode_only
def remove_people():
    database.session.query(Person).delete()
    database.session.commit()

    msg = {"msg": "all people deleted"}

    return jsonify(msg)


@admin.route("/remove-transactions", methods=["GET"])
@login_required
@development_mode_only
def remove_transactions():
    database.session.query(Transaction).delete()
    database.session.commit()

    msg = {"msg": "all transactions deleted"}

    return jsonify(msg)


@admin.route("/delete-connect-account", methods=["GET"])
@login_required
@development_mode_only
def delete_connect_account():
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


@admin.route("/remove-documents", methods=["GET"])
@login_required
@development_mode_only
def remove_documents():
    Document.query.where(Document.type == "terms-and-conditions-agreed").delete()
    database.session.commit()

    msg = {"msg": "all documents deleted"}

    return jsonify(msg)
