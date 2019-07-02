import subscribie

@pytest.fixture
def app():
  return subscribie.create_app()

@pytest.fixture
def client(app):
  client = app.test_client()
  return client

def test_homepage(client):
  req = client.get("/")
  assert req.status_code == 200
