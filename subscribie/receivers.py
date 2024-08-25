import logging
from subscribie.tasks import background_task
from subscribie.email import (
    send_donation_thankyou_email,
    send_welcome_email,
)
from subscribie.notifications import (
    subscriberPaymentFailedNotification,
    newSubscriberEmailNotification,
)
from subscribie.models import Subscription, Document, Integration
from subscribie.database import database
import sqlalchemy
import requests
from requests.auth import HTTPBasicAuth


log = logging.getLogger(__name__)


def receiver_attach_documents_to_subscription(*args, **kwargs):
    subscription_uuid = kwargs.get("subscription_uuid")
    is_donation = kwargs.get("is_donation")
    if subscription_uuid is None and is_donation is True:
        log.error(
            "The checkout was a donation and therefore it can't have a document attached"  # noqa: E501
        )
        return None

    elif subscription_uuid is None:
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


def receiver_new_subscriber(*args, **kwargs):
    subscription_uuid = kwargs.get("subscription_uuid")
    subscription = None
    try:
        subscription = (
            Subscription.query.where(Subscription.uuid == subscription_uuid)
            .execution_options(include_archived=True)
            .one()
        )
        subscriber_email = subscription.person.email
    except sqlalchemy.exc.NoResultFound:
        if subscription is None and subscription_uuid != "test":
            msg = "Got receiver_new_subscriber event but no associated subscription found."  # noqa: E501
            log.error(msg)
            return
        elif subscription_uuid == "test":
            log.info("Testing receiver_new_subscriber with dummy subscription")
            subscriber_email = "test-subscriber@example.com"

    kwargs = {}
    kwargs["subscription_uuid"] = subscription_uuid
    kwargs["subscriber_email"] = subscriber_email
    kwargs["subscription"] = subscription

    send_welcome_email(to_email=subscriber_email, subscription=subscription)
    newSubscriberEmailNotification(**kwargs)


def receiver_new_subscriber_send_to_mailchimp(*args, **kwargs) -> None:
    """
    Send new subscriber contact information to Mainchimp.
    For this to work, Subscribie needs to have:

    - Mailchimp api key
    - Mainchimp Audience id (maichimp lets you add contacts
        to *audiences* (aka lists), not simply one large pot
        of contacts- which is good.
    - It is the responsibility of the Shop owner to create the
    Mailchimp api key, and Audience within their Mailchimp account.
    Then, the shop own must input these items (MailChimp API key,
    and audience id) into their Subscribie shop, under 'integrations'.
    """

    integration = Integration.query.first()
    if integration.mailchimp_active is False:
        log.debug(
            """Refusing receiver_new_subscriber_send_to_mailchimp because
            integration.mailchimp_active is false"""
        )
        return None
    mailchimp_api_key, dc = integration.mailchimp_api_key.split("-")
    mailchimp_list_id = integration.mailchimp_list_id

    subscription_uuid = kwargs.get("subscription_uuid")
    subscription = None
    try:
        subscription = (
            Subscription.query.where(Subscription.uuid == subscription_uuid)
            .execution_options(include_archived=True)
            .one()
        )
        subscriber_email = subscription.person.email
        # Send subscriber to mailchimp audience
        data = {
            "email_address": subscriber_email,
            "status": "subscribed",
            "merge_fields": {
                "FNAME": subscription.person.given_name,
                "LNAME": subscription.person.family_name,
            },
            "tags": ["subscribie"],
        }

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
            log.debug("Success adding subscriber to mailchimp audience.")
        elif (
            response.status_code == 400 and response.json()["title"] == "Member Exists"
        ):
            log.debug("Member already exists in list")
        else:
            log.error(
                f"Failed to add member to the list. Status code: {response.status_code}"
            )
    except sqlalchemy.exc.NoResultFound:
        if subscription is None and subscription_uuid != "test":
            msg = "Got receiver_new_subscriber_send_to_mailchimp event but no associated subscription found."  # noqa: E501
            log.error(msg)
            return
    except Exception as e:
        log.error(f"Unable to receiver_new_subscriber_send_to_mailchimp: {e}")


def receiver_new_donation(*args, **kwargs):
    to_email = kwargs.get("email")
    send_donation_thankyou_email(to_email=to_email)
