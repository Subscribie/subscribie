from subscribie.database import database
from subscribie.models import Person, Subscription, Plan, PlanRequirements, Transaction
from sqlalchemy.sql import func
import logging


log = logging.getLogger(__name__)


def get_number_of_active_subscribers():
    count = 0
    subscribers_with_subscriptions = (
        database.session.query(Person)
        .join(Subscription)
        .join(Plan, Subscription.sku_uuid == Plan.uuid)
        .join(PlanRequirements, Plan.id == PlanRequirements.plan_id)
        .filter(PlanRequirements.subscription == 1)
    )
    # Check if their subscriptions are active
    for subscriber in subscribers_with_subscriptions:
        # Check each subscibers subscriptions to see if they're active
        for subscription in subscriber.subscriptions:
            if subscription.stripe_subscription_active():
                log.info(
                    f"Checking if subscription {subscription.stripe_subscription_id} is active"  # noqa: E501
                )
                count += 1
    return count


def get_monthly_revenue():
    query = (
        database.session.query(func.sum(Plan.interval_amount))
        .join(Subscription, Plan.uuid == Subscription.sku_uuid)
        .where(Subscription.stripe_status == "active")
        .where(Plan.interval_unit == "monthly")
        .execution_options(include_archived=True)
    )
    monthly_revenue = query.first()[0]
    if monthly_revenue is None:
        return 0
    else:
        return monthly_revenue / 100


def get_number_of_subscribers():
    """Returns number of subscribers, including subscribers with inactive subscriptions"""  # noqa: E501
    count = (
        database.session.query(Person)
        .join(Subscription)
        .join(Plan, Subscription.sku_uuid == Plan.uuid)
        .join(PlanRequirements, Plan.id == PlanRequirements.plan_id)
        .filter(PlanRequirements.subscription == 1)
        .count()
    )
    return count


def get_number_of_signups():
    """Returns number of subscribers, either signing up with subscription OR one-off payment"""  # noqa: E501
    count = (
        database.session.query(Person)
        .join(Subscription)
        .join(Plan, Subscription.sku_uuid == Plan.uuid)
        .join(PlanRequirements, Plan.id == PlanRequirements.plan_id)
        .count()
    )
    return count


def get_number_of_one_off_purchases():
    """Returns number of people who completed a one-off payment"""  # noqa: E501
    count = (
        database.session.query(Person)
        .join(Subscription)
        .join(Plan, Subscription.sku_uuid == Plan.uuid)
        .join(PlanRequirements, Plan.id == PlanRequirements.plan_id)
        .filter(PlanRequirements.subscription == 0)
        .filter(PlanRequirements.instant_payment == 1)
        .count()
    )
    return count


def get_number_of_transactions_with_donations():
    count = (
        database.session.query(Person)
        .join(Transaction)
        .filter(Transaction.is_donation == 1)
        .count()
    )
    return count
