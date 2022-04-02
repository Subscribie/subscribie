import logging
from subscribie.tasks import task_queue, background_task
from subscribie.notifications import subscriberPaymentFailedNotification
from subscribie.models import User, Company
import smtplib
import socket
from dotenv import load_dotenv
from email.mime.text import MIMEText
import os

load_dotenv(verbose=True)

log = logging.getLogger(__name__)


def receiver_send_shop_owner_new_subscriber_notification_email(
    sender, email=None, **kwargs
):
    def send_shop_owner_notification_email(receiver=None, company_name=None):
        mail_server_host = os.getenv("MAIL_SERVER", None)
        port = os.getenv("MAIL_PORT", None)
        sender = os.getenv("MAIL_DEFAULT_SENDER", None)

        msg = MIMEText(
            f"""You have a new subscriber on your Subscribie shop: {company_name}.\n\nLogin to your shop to see more."""  # noqa
        )

        msg["Subject"] = "Subscribie: New Subscriber"
        msg["From"] = os.getenv("MAIL_DEFAULT_SENDER", None)
        msg["To"] = receiver

        user = os.getenv("MAIL_DEFAULT_SENDER", None)
        password = os.getenv("MAIL_PASSWORD", None)

        try:
            with smtplib.SMTP(mail_server_host, port) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(sender, receiver, msg.as_string())
                log.info(
                    "Sent receiver_send_shop_owner_new_subscriber_notification_email"
                )
        except ConnectionRefusedError as e:
            log.error(f"Could not send email. ConnectionRefusedError: {e}")
        except socket.gaierror as e:
            log.error(f"Could not send email. socket.gaierror: {e}")
        except OSError as e:
            log.error(f"Could not send email. OSError: {e}")

    email = User.query.first().email  # Get email address of shop owner
    company_name = Company.query.first().name
    task_queue.put(
        lambda: send_shop_owner_notification_email(
            receiver=email, company_name=company_name
        )
    )


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
