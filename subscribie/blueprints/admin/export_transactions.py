from . import admin
from subscribie.auth import login_required
from subscribie.database import database
from subscribie.models import Transaction
from flask import request, Response, jsonify
import logging


log = logging.getLogger(__name__)


@admin.route("/export-transactions")
@login_required
def export_transactions():

    transactions = database.session.query(Transaction).all()

    if len(transactions) == 0:
        return "You don't have any transactions yet."
    rows = []
    for transaction in transactions:
        if transaction.person is not None:
            rows.append(
                {
                    "given_name": transaction.person.given_name,
                    "family_name": transaction.person.family_name,
                    "email": transaction.person.email,
                    "plan": "Unknown"
                    if transaction.subscription.plan is None
                    else transaction.subscription.plan.title,
                    "subscription_status": transaction.subscription.stripe_status,
                }
            )
        else:
            log.info(f"Excluding transaction {transaction.id} as no person attached")

    if "csv" in request.args:
        import csv
        import io

        outfile = io.StringIO()
        outcsv = csv.DictWriter(outfile, fieldnames=transactions[0].keys())
        outcsv.writeheader()
        for row in rows:
            outcsv.writerow(row)

        return Response(
            outfile.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=transactions.csv"},
        )

    return jsonify(rows)
