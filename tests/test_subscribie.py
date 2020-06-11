import pytest
from subscribie.models import User

from contextlib import contextmanager
from flask import appcontext_pushed, g

@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user
    with appcontext_pushed.connected_to(handler, app):
        yield

def test_admin_can_view_dashboard(session, app, client, admin_session):
    user = User.query.filter_by(email='admin@example.com').first()
    with user_set(app, user):
        req = client.get("/admin/dashboard", follow_redirects=True)


@pytest.fixture(scope='function')
def admin_session(client, with_shop_owner):
    user = User.query.filter_by(email='admin@example.com').first()
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin@example.com'


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
