from . import database
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from uuid import uuid4

class User(database.Model):
    __tablename__ = 'user'
    id = database.Column(database.Integer(), primary_key=True)
    email = database.Column(database.String())
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    active = database.Column(database.String)
    login_token = database.Column(database.String)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Person(database.Model):
    __tablename__ = 'person'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=str(uuid4()))
    sid = database.Column(database.String())
    ts = database.Column(database.DateTime, default=datetime.utcnow)
    given_name = database.Column(database.String())
    family_name = database.Column(database.String())
    address_line1 = database.Column(database.String())
    city = database.Column(database.String())
    postal_code = database.Column(database.String())
    email = database.Column(database.String())
    mobile = database.Column(database.String())
    subscriptions = relationship("Subscription", back_populates="person")
    transactions = relationship("Transaction", back_populates="person")

    def __repr__(self):
        return '<Person {}>'.format(self.given_name)

class Subscription(database.Model):
    __tablename__ = 'subscription'
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=str(uuid4()))
    sku_uuid = database.Column(database.String())
    gocardless_subscription_id = database.Column(database.String())
    person_id = database.Column(database.Integer(), ForeignKey('person.id'))
    item = relationship("Item", uselist=False, primaryjoin="foreign(Item.uuid)==Subscription.sku_uuid")
    person = relationship("Person", back_populates="subscriptions")
    note = relationship("SubscriptionNote", back_populates="subscription")
    created_at = database.Column(database.DateTime, default=datetime.utcnow)

class SubscriptionNote(database.Model):
    __tablename__ = 'subscription_note'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    note = database.Column(database.String())
    subscription_id = database.Column(database.Integer(), ForeignKey('subscription.id'))
    subscription = relationship("Subscription", back_populates="note")

class Company(database.Model):
    __tablename__ = 'company'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    name = database.Column(database.String())
    slogan = database.Column(database.String())

class Item(database.Model):
    __tablename__ = 'item'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    archived = database.Column(database.Boolean(), default=False)
    uuid = database.Column(database.String(), default=str(uuid4()))
    title = database.Column(database.String())
    monthly_price = database.Column(database.Integer())
    sell_price = database.Column(database.Integer())
    days_before_first_charge = database.Column(database.Integer())
    primary_icon = database.Column(database.String())
    requirements = relationship("ItemRequirements", back_populates="item")
    selling_points = relationship("ItemSellingPoints", back_populates="item")

class ItemRequirements(database.Model):
    __tablename__ = 'item_requirements'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    item_id = database.Column(database.Integer(), ForeignKey('item.id'))
    item = relationship("Item", back_populates="requirements")
    instant_payment = database.Column(database.Boolean(), default=False)
    subscription = database.Column(database.Boolean(), default=False)
    note_to_seller_required = database.Column(database.Boolean(), default=False)
    note_to_buyer_message = database.Column(database.String())

class ItemSellingPoints(database.Model):
    __tablename__ = 'item_selling_points'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    point = database.Column(database.String())
    item_id = database.Column(database.Integer(), ForeignKey('item.id'))
    item = relationship("Item", back_populates="selling_points")

class Integration(database.Model):
    __tablename__ = 'integration'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    google_tag_manager_active = database.Column(database.Boolean())
    google_tag_manager_container_id = database.Column(database.String())
    tawk_active = database.Column(database.Boolean())
    tawk_property_id = database.Column(database.String())

class PaymentProvider(database.Model):
    __tablename__ = 'payment_provider'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    gocardless_active = database.Column(database.Boolean())
    gocardless_access_token = database.Column(database.String())
    gocardless_environment = database.Column(database.String())
    stripe_active = database.Column(database.Boolean())
    stripe_publishable_key = database.Column(database.String())
    stripe_secret_key = database.Column(database.String())

class Page(database.Model):
    __tablename__ = 'page'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    page_name = database.Column(database.String())
    path = database.Column(database.String())
    template_file = database.Column(database.String())

class Module(database.Model):
    __tablename__ = 'module'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    name = database.Column(database.String())
    src = database.Column(database.String())

class Transaction(database.Model):
    __tablename__ = 'transactions'
    id = database.Column(database.Integer(), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    uuid = database.Column(database.String(), default=str(uuid4()))
    amount = database.Column(database.Integer())
    comment = database.Column(database.Text())
    # External id e.g. Stripe or GoCardless id
    external_id = database.Column(database.String())
    # Source of transaction e.g. Stripe or GoCardless
    external_src = database.Column(database.String())
    person_id = database.Column(database.Integer(), ForeignKey('person.id'))
    person = relationship("Person", back_populates="transactions")

