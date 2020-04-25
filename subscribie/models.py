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

    def __repr__(self):
        return '<Person {}>'.format(self.given_name)

class Subscription(database.Model):
    __tablename__ = 'subscription'
    id = database.Column(database.Integer(), primary_key=True)
    uuid = database.Column(database.String(), default=str(uuid4()))
    sku_uuid = database.Column(database.String())
    gocardless_subscription_id = database.Column(database.String())
    person_id = database.Column(database.Integer(), ForeignKey('person.id'))
    person = relationship("Person", back_populates="subscriptions")
    created_at = database.Column(database.DateTime, default=datetime.utcnow)

