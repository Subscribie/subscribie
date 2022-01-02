from . import admin
from subscribie.auth import login_required
from subscribie.models import Transaction
from flask import request, Response, jsonify
import logging


log = logging.getLogger(__name__)


@admin.route("/export-transactions")
@login_required
def export_transactions():

    transactions = Transaction.query.execution_options(include_archived=True).all()

    if len(transactions) == 0:
        return "You don't have any transactions yet."
    rows = []
    for transaction in transactions:
        if transaction.person is not None:
            rows.append(
                {
                    "transaction_date": transaction.created_at,
                    "amount": transaction.amount / 100,
                    "currency": "GBP",
                    "payment_status": transaction.payment_status,
                    "subscription_status": transaction.subscription.stripe_status,
                    "plan_title": transaction.subscription.plan.title,
                    "given_name": transaction.person.given_name,
                    "family_name": transaction.person.family_name,
                    "email": transaction.person.email,
                    "subscribie_transaction_reference": transaction.uuid,
                    "subscribie_external_src": transaction.external_src,
                    "subscribie_external_id": transaction.external_id
                }
            )
        else:
            log.info(f"Excluding transaction {transaction.id} as no person attached")

    if "csv" in request.args:
        import csv
        import io

        outfile = io.StringIO()
        outcsv = csv.DictWriter(outfile, fieldnames=rows[0].keys())
        outcsv.writeheader()
        for row in rows:
            outcsv.writerow(row)

        return Response(
            outfile.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=transactions.csv"},
        )

    return jsonify(rows)
