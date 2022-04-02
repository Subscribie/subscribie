import logging
from subscribie.tasks import task_queue, background_task
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
    log.debug("In receiver_send_subscriber_payment_failed_notification_email")
    breakpoint()
    pass
