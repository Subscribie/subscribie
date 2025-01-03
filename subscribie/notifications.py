import logging

from flask import current_app
from .email import EmailMessageQueue
from subscribie.models import Company, Setting, User
from subscribie.tasks import background_task
from jinja2 import Template
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)


def newSubscriberEmailNotification(*args, **kwargs):
    """As a shop owner all shop admins email notification
    when a new subscriber joins
    https://github.com/Subscribie/subscribie/issues/602
    """
    try:
        company = Company.query.first()
        msg = EmailMessageQueue()
        subscriber_email = kwargs.get("subscriber_email")
        log.debug(
            f"newSubscriberEmailNotification subscriber_email is: {subscriber_email}"
        )
        msg["subject"] = f"{company.name} - new subscriber ({subscriber_email})"
        msg["from"] = current_app.config["EMAIL_LOGIN_FROM"]
        shop_admins = User.query.all()  # all shop admins
        msg["to"] = [user.email for user in shop_admins]  # all shop admins
        # use user-new-subscriber-notification.jinja2.html
        email_template = str(
            Path(
                current_app.root_path
                + "/emails/user-new-subscriber-notification.jinja2.html"
            )
        )
        with open(email_template) as file_:
            template = Template(file_.read())
            html = template.render(**kwargs)
            msg.add_alternative(html, subtype="html")
            log.debug(
                f"newSubscriberEmailNotification rendered as:\nSubject: {msg['subject']}\n{html}"  # noqa: E501
            )
        setting = Setting.query.first()
        if setting.reply_to_email_address is not None:
            msg["reply-to"] = setting.reply_to_email_address
        else:
            msg["reply-to"] = User.query.first().email
        log.info("queueing new subscriber notification email")
        msg.queue()
    except Exception as e:
        log.error(f"failed to send newSubscriberEmailNotification email: {e}")


@background_task
def newSubscriberSendToMailchimpNotification(
    subscriber_email: str,
    mailchimp_list_id: str,
    data: dict,
    mailchimp_api_key: str,
    dc: str,
    *args,
    **kwargs,
) -> bool:
    log.debug("newSubscriberSendToMailchimpNotification called")

    # Post to Mailchimp lists endpoint
    url = f"https://{dc}.api.mailchimp.com/3.0/lists/{mailchimp_list_id}/members"
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        url,
        headers=headers,
        auth=HTTPBasicAuth("key", mailchimp_api_key),
        json=data,
    )

    if response.status_code == 200:
        log.debug(
            f"Success adding subscriber to mailchimp audience."
            f"Response: {response.text}"
        )
    elif response.status_code == 400 and response.json()["title"] == "Member Exists":
        log.debug("Member already exists in list")
        return False
    else:
        log.error(
            f"Failed to add member to the list. Status code: {response.status_code}."
            f"Response: {response.text}"
        )
        return False
    log.debug("newSubscriberSendToMailchimpNotification completed")
    return True


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
            kwargs["subscriber_login_url"] = (
                f"https://{app.config['SERVER_NAME']}/account/login"
            )
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
