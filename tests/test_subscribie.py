import pytest
import subscribie
from subscribie.models import User

def test_homepage(session, client):
  req = client.get("/")
  assert req.status_code == 200

def test_magic_login_submission_as_shop_owner(session, client, with_shop_owner):
    """This does not test a successful login. Only that the login form submission
        is working.
    
        As a shop owner, when I submit an email address to the login form,
       the form submission succeeds.
    """
    req = client.post("/auth/login", data=dict(email='admin@example.com'))
    assert b"We've just sent you a login link." in req.data

def test_user_model(session):
    user = User()
    user.email = "test@example.com"
    session.add(user)
    session.commit()
    assert user.id > 0
