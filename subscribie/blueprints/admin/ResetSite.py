import os
from . import admin
from subscribie.auth import login_required
from subscribie.database import database
from subscribie.models import Subscription, Person, Transaction
from flask import jsonify


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
