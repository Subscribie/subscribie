import pytest
import subscribie
from subscribie.models import User

def test_homepage(session, client):
  req = client.get("/")
  assert req.status_code == 200

def test_user_model(session):
    user = User()
    user.email = "test@example.com"
    session.add(user)
    session.commit()
    assert user.id > 0
