import logging
from subscribie.tasks import background_task
from subscribie.email import send_welcome_email
from subscribie.notifications import subscriberPaymentFailedNotification
from subscribie.models import Subscription, Document
from subscribie.database import database
from dotenv import load_dotenv
import sqlalchemy

load_dotenv(verbose=True)

log = logging.getLogger(__name__)


def receiver_attach_documents_to_subscription(*args, **kwargs):
    subscription_uuid = kwargs.get("subscription_uuid")
    if subscription_uuid is None:
        log.error(
            "receiver_attach_documents_to_subscription called but no subscription_uuid was given in the signal"  # noqa: E501
        )
        return None

    subscription = (
        Subscription.query.where(Subscription.uuid == subscription_uuid)
        .execution_options(include_archived=True)  # to include archived Documents
        .one()
    )

    # If associated plan has document(s) associated,
    # then copy those docs to preserve them as a
    # system of record, and assignment to the
    # subscription.documents
    if len(subscription.plan.documents) > 0:
        for document in subscription.plan.documents:
            # Create copy of Document and assign it to Subscription
            newDoc = Document()
            newDoc.name = document.name

            # If is a terms-and-conditions-document change the document
            # from terms-and-conditions to terms-and-conditions-agreed
            # otherwise keep the type of the document
            if document.type == "terms-and-conditions":
                newDoc.type = "terms-and-conditions-agreed"
            else:
                newDoc.type = document.type

            newDoc.body = document.body
            newDoc.read_only = (
                True  # Mark Document as read-only (since its been signed up to)
            )
            subscription.documents.append(newDoc)
            try:
                database.session.commit()
            except sqlalchemy.exc.IntegrityError as e:
                # Document is already assigned to Subscription
                database.session.rollback()
                log.error(e)


@background_task
def receiver_send_subscriber_payment_failed_notification_email(*args, **kwargs):
    """Recieve stripe payment_intent.payment_failed signal"""
    log.debug("In receiver_send_subscriber_payment_failed_notification_email")
    if "stripe_event" not in kwargs:
        log.error(
            "No stripe_event passed to receiver_send_shop_owner_new_subscriber_notification_email"  # noqa: E501
        )
        return 255

    # Get event information from the received stripe_event & send email
    # notification to subscriber about failed payment
    # See https://stripe.com/docs/declines/codes
    # and https://stripe.com/docs/api/charges/object#charge_object-failure_code

    stripe_event = kwargs["stripe_event"]

    messageKwArgs = {}
    messageKwArgs["failure_message"] = stripe_event["charges"]["data"][0][
        "failure_message"
    ]
    messageKwArgs["failure_code"] = stripe_event["charges"]["data"][0]["failure_code"]
    messageKwArgs["subscriber_email"] = stripe_event["charges"]["data"][0][
        "billing_details"
    ]["email"]
    messageKwArgs["subscriber_name"] = stripe_event["charges"]["data"][0][
        "billing_details"
    ]["name"]
    messageKwArgs["app"] = kwargs["app"]

    # Send email notification to subscriber
    subscriberPaymentFailedNotification(**messageKwArgs)


def receiver_send_welcome_email(*args, **kwargs):
    to_email = kwargs.get("email")
    send_welcome_email(to_email=to_email)
