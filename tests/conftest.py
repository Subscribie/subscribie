import os
import pytest

from flask_migrate import upgrade
from flask_migrate import Migrate

from subscribie import create_app
from subscribie.models import User, Company, Setting
from subscribie import seed_db
from sqlalchemy.orm import scoped_session, sessionmaker


TESTDB = "test_project.db"
TESTDB_PATH = "/tmp/{}".format(TESTDB)
TEST_DATABASE_URI = "sqlite:///" + TESTDB_PATH


@pytest.fixture(scope="session")
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SQLALCHEMY_DATABASE_URI": TEST_DATABASE_URI,
        "DB_FULL_PATH": TESTDB_PATH,
    }
    app = create_app(settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture
def client(app):
    client = app.test_client()
    return client


def apply_migrations(app):
    """Applies all alembic migrations."""
    from subscribie import database as db
    Migrate(app, db)
    upgrade("./migrations")
    seed_db()


@pytest.fixture(scope="session")
def db_session(app, request):
    """Creates a new database session for a test."""
    from subscribie import database as db

    connection = db.engine.connect()
    transaction = connection.begin()
    session = scoped_session(sessionmaker(bind=connection))

    db.session = session
    apply_migrations(app)

    def teardown():
        transaction.rollback()
        connection.close()
        connection.engine.dispose()
        session.close()
        session.remove()
        if os.path.exists(TESTDB_PATH):
            os.unlink(TESTDB_PATH)

    request.addfinalizer(teardown)
    return session


@pytest.fixture(scope="function")
def with_shop_owner(db_session):
    user = User()
    user.email = "admin@example.com"
    db_session.add(user)
    # Add a company
    company = Company()
    company.name = "Subscription Shop"
    company.slogan = "Buy plans on subscription"
    db_session.commit()


@pytest.fixture(scope="function")
def with_default_country_code_and_default_currency(db_session):
    # Add minimal settings
    setting = Setting()
    setting.default_currency = "GBP"
    setting.default_country_code = "GB"
    db_session.add(setting)
    db_session.commit()
