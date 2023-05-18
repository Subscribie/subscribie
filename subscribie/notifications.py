import logging

from flask import current_app
from .email import EmailMessageQueue
from subscribie.models import Company, Setting, User
from jinja2 import Template
from pathlib import Path

log = logging.getLogger(__name__)


def newSubscriberEmailNotification(*args, **kwargs):
    """As a shop owner all shop admins email notification
    when a new subscriber joins
    https://github.com/Subscribie/subscribie/issues/602
    """
    try:
        company = Company.query.first()
        msg = EmailMessageQueue()
        msg["subject"] = f"{company.name} - new subscriber"
        msg["from"] = current_app.config["EMAIL_LOGIN_FROM"]
        shopadmins = User.query.all()  # all shop admins
        msg["to"] = [user.email for user in shopadmins]  # all shop admins
        msg.set_content("you have a new subscriber!")
        setting = Setting.query.first()
        if setting.reply_to_email_address is not None:
            msg["reply-to"] = setting.reply_to_email_address
        else:
            msg["reply-to"] = User.query.first().email
        log.info("queueing new subscriber notification email")
        msg.queue()
    except Exception as e:
        log.error(f"failed to send newsubscriberemailnotification email: {e}")


def subscriberPaymentFailedNotification(
    subscriber_email=None,
    subscriber_name=None,
    failure_message=None,
    failure_code=None,
    **kwargs,
):
    """As a Subscriber I am notified if I owe money
    to the shop plan I'm subscribed to (e.g if I
    fail a payment/failed payment.

    https://github.com/Subscribie/subscribie/pull/848
    """
    try:
        app = kwargs["app"]
        with app.app_context():
            company = Company.query.first()
            kwargs["company"] = company
            kwargs["subscriber_email"] = subscriber_email
            kwargs["subscriber_name"] = subscriber_name
            kwargs["subscriber_first_name"] = subscriber_name.split(" ")[0]
            kwargs["failure_message"] = failure_message
            kwargs["failure_code"] = failure_code
            kwargs[
                "subscriber_login_url"
            ] = f"https://{app.config['SERVER_NAME']}/account/login"
            msg = EmailMessageQueue()
            msg["subject"] = f"{company.name} - A payment collection failed"
            msg["from"] = current_app.config["EMAIL_LOGIN_FROM"]
            msg["to"] = [subscriber_email]  # all shop admins
            # use subscriber-payment-failed-notification.jinja2.html
            email_template = str(
                Path(
                    app.root_path
                    + "/emails/subscriber-payment-failed-notification.jinja2.html"
                )
            )
            with open(email_template) as file_:
                template = Template(file_.read())
                html = template.render(**kwargs)
                msg.add_alternative(html, subtype="html")

            setting = Setting.query.first()
            if setting.reply_to_email_address is not None:
                msg["reply-to"] = Setting.reply_to_email_address
            else:
                msg["reply-to"] = User.query.first().email
            log.info("queueing subscriber payment failed notification email")
            msg.queue()
    except Exception as e:
        log.error(f"failed to send subscriberPaymentFailedNotification email: {e}")
