from . import admin
from subscribie.auth import login_required
from subscribie.models import Subscription
from flask import request, Response, jsonify
import logging
import json


@admin.route("/export-subscribers-email")
@login_required
def export_subscribers():
    subscriptions = Subscription.query.execution_options(include_archived=True).all()

    if len(subscriptions) == 0:
        return "You don't have any subscribers yet."
    subscribers = []
    all_fieldnames = set()
    for subscription in subscriptions:
        if subscription.person is not None:
            person = {
                "person_created_at_date": subscription.person.created_at.strftime(
                    "%d-%m-%Y"
                ),  # noqa: E501
                "person_created_at_time": subscription.person.created_at.strftime(
                    "%H:%M"
                ),  # noqa: E501
                "given_name": subscription.person.given_name,
                "family_name": subscription.person.family_name,
                "email": subscription.person.email,
                "plan": subscription.plan.title,
                "subscription_status": subscription.stripe_status,
            }
            # Include subscription question answers in export, if any
            if subscription.question_answers:
                for answer in subscription.question_answers:
                    field_name = f"question_id-{answer.question_id}-{json.dumps(answer.question_title)}"  # noqa: E501
                    person[field_name] = json.dumps(answer.response)
                    all_fieldnames.add(field_name)
            subscribers.append(person)
            # Collect static fieldnames
            all_fieldnames.update(person.keys())
        else:
            logging.info(
                f"Excluding subscription {subscription.id} as no person attached"
            )

    if "csv" in request.args:
        import csv
        import io

        outfile = io.StringIO()
        outcsv = csv.DictWriter(
            outfile, fieldnames=list(sorted(all_fieldnames)), extrasaction="ignore"
        )
        outcsv.writeheader()
        for subscriber in subscribers:
            outcsv.writerow(subscriber)

        return Response(
            outfile.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=subscribers.csv"},
        )

    return jsonify(subscribers)
