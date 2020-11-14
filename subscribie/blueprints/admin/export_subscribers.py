from . import admin
from subscribie.auth import login_required
from subscribie.database import database
from subscribie.models import Subscription
from flask import request, Response, jsonify


@admin.route("/export-subscribers-email")
@login_required
def export_subscribers():

    subscriptions = database.session.query(Subscription).all()

    if len(subscriptions) == 0:
        return "You don't have any subscribers yet."
    subscribers = []
    for subscription in subscriptions:
        subscribers.append(
            {
                "given_name": subscription.person.given_name,
                "family_name": subscription.person.family_name,
                "email": subscription.person.email,
            }
        )

    if "csv" in request.args:
        import csv
        import io

        outfile = io.StringIO()
        outcsv = csv.DictWriter(outfile, fieldnames=subscribers[0].keys())
        outcsv.writeheader()
        for subscriber in subscribers:
            outcsv.writerow(subscriber)

        return Response(
            outfile.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=subscribers.csv"},
        )
        return outfile.getvalue()

    return jsonify(subscribers)