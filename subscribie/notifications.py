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
        msg["Subject"] = f"{company.name} - New Subscriber"
        msg["From"] = current_app.config["EMAIL_LOGIN_FROM"]
        shopAdmins = User.query.all()  # All shop admins
        msg["To"] = [user.email for user in shopAdmins]  # All shop admins
        msg.set_content("You have a new subscriber on your shop!")
        setting = Setting.query.first()
        if setting is not None:
            msg["Reply-To"] = setting.reply_to_email_address
        else:
            msg["Reply-To"] = User.query.first().email
        log.info("Queueing new subscriber notification email")
        msg.queue()
    except Exception as e:
        log.error(f"Failed to send newSubscriberEmailNotification email: {e}")
