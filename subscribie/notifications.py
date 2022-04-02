import logging

from flask import current_app
from .email import EmailMessageQueue
from subscribie.models import Company, Setting, User

log = logging.getLogger(__name__)


def newSubscriberEmailNotification():
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
    subscriber_email=None, failure_message=None, failure_code=None, **kwargs
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
            msg = EmailMessageQueue()
            msg["subject"] = f"{company.name} - A payment collection failed"
            msg["from"] = current_app.config["EMAIL_LOGIN_FROM"]
            msg["to"] = [subscriber_email]  # all shop admins
            msg.set_content(
                f'A payment collection failed for {company.name}\nThe bank gave the following reason: "{failure_message} / {failure_code}."\nPlease could you log into your account and check your payment details?\nYou can also retry payments from there too.\n Thank you!'  # noqa: E501
            )
            setting = Setting.query.first()
            if setting.reply_to_email_address is not None:
                msg["reply-to"] = Setting.reply_to_email_address
            else:
                msg["reply-to"] = User.query.first().email
            log.info("queueing subscriber payment failed notification email")
            msg.queue()
    except Exception as e:
        log.error(f"failed to send subscriberPaymentFailedNotification email: {e}")
