import logging
from subscribie.tasks import background_task
from subscribie.notifications import subscriberPaymentFailedNotification
from dotenv import load_dotenv

load_dotenv(verbose=True)

log = logging.getLogger(__name__)


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
