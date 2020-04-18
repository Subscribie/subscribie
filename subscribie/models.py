from . import database
from datetime import datetime

class User(database.Model):
    __tablename__ = 'user'
    email = database.Column(database.String(255), primary_key=True)
    created_at = database.Column(database.DateTime, default=datetime.utcnow)
    active = database.Column(database.String)
    login_token = database.Column(database.String)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class Person(database.Model):
    __tablename__ = 'person'
    sid = database.Column(database.String(), primary_key=True)
    ts = database.Column(database.DateTime, default=datetime.utcnow)
    given_name = database.Column(database.String())
    family_name = database.Column(database.String())
    address_line1 = database.Column(database.String())
    city = database.Column(database.String())
    postal_code = database.Column(database.String())
    email = database.Column(database.String())
    mobile = database.Column(database.String())

    def __repr__(self):
        return '<Person {}>'.format(self.given_name)
