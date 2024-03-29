from . import admin
from subscribie.auth import login_required
from subscribie.models import Transaction
from subscribie.database import database

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
        subscription_note = "None"
        if transaction.person is not None:
            # Transactions without an associated subscription (e.g.
            # a manual charge to a customer, will not have an associated
            # subscription.
            if transaction.subscription:
                plan_title = transaction.subscription.plan.title
                subscription_uuid = transaction.subscription.uuid
                subscription_status = transaction.subscription.stripe_status
                if transaction.subscription.note and isinstance(
                    transaction.subscription.note.note, str
                ):
                    subscription_note = (
                        transaction.subscription.note.note.strip().replace(",", ";")
                    )
            else:
                plan_title = None
                subscription_uuid = None
                subscription_status = None
            # Backward compatibility to GB only shops
            # TODO Remove
            if transaction.is_donation is None:
                transaction.is_donation = False

            if transaction.currency is None:
                transaction.currency = "GBP"
                try:
                    database.session.commit()
                except Exception as e:
                    log.error(f"Problem committing transaction currency null: {e}")
            rows.append(
                {
                    "transaction_date": transaction.created_at,
                    "plan_title": plan_title,
                    "amount": transaction.amount / 100,
                    "currency": transaction.currency.upper(),
                    "payment_status": transaction.payment_status,
                    "given_name": transaction.person.given_name,
                    "family_name": transaction.person.family_name,
                    "email": transaction.person.email,
                    "subscription_status": subscription_status,
                    "comment": transaction.comment,
                    "subscription_uuid": subscription_uuid,
                    "subscribie_transaction_uuid": transaction.uuid,
                    "subscribie_external_src": transaction.external_src,
                    "subscribie_external_id": transaction.external_id,
                    "is_donation": transaction.is_donation,
                    "subscription_note": subscription_note,
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
