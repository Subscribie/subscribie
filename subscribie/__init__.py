# -*- coding: utf-8 -*-
"""
    subscribie.app
    ~~~~~~~~~
    A microframework for building Subscription websites.
    This module implements the central subscribie application.

    :copyright: (c) 2018 by Karma Computing Ltd
"""
import sentry_sdk
from subscribie.settings import settings
from .logger import logger  # noqa: F401
import logging
import os
import sys
import sqlite3
from .database import database
from base64 import b64encode
from flask import (
    Flask,
    render_template,
    session,
    url_for,
    current_app,
    Blueprint,
    request,
    abort,
)

sentry_sdk.init(
    dsn=settings.get("SENTRY_SDK_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)
from flask_babel import Babel, _
from subscribie.email import EmailMessageQueue
from .Template import load_theme
from flask_cors import CORS
from flask_uploads import (
    configure_uploads,
    UploadSet,
    IMAGES,
)  # noqa: E501
import importlib
import urllib
from pathlib import Path
from importlib.resources import files, as_file
import sqlalchemy
from flask_migrate import Migrate, upgrade
import click
from jinja2 import Template
from .models import (
    PaymentProvider,
    Person,
    Company,
    Module,
    Plan,
    PriceList,
)
from subscribie.utils import (
    backfill_transactions as call_backfill_transactions,
    backfill_subscriptions as call_backfill_subscriptions,
    backfill_persons as call_backfill_persons,
    backfill_stripe_invoices as call_backfill_stripe_invoices,
)
from datetime import datetime

log = logging.getLogger(__name__)


def seed_db():
    pass


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.update(settings)
    LANGUAGES = ["en", "de", "es", "fr", "hr"]
    PERMANENT_SESSION_LIFETIME = int(os.environ.pop("PERMANENT_SESSION_LIFETIME", 1800))
    app.config.update(os.environ)
    app.config["PERMANENT_SESSION_LIFETIME"] = PERMANENT_SESSION_LIFETIME
    app.config["MAX_CONTENT_LENGTH"] = int(settings.get("MAX_CONTENT_LENGTH", 52428800))

    if test_config is not None:
        app.config.update(test_config)

    def get_locale():
        language_code = session.get("language_code", None)
        if language_code is not None:
            log.info(f"language_code has been manually set to: {language_code}")
        # if language_code not none and is a supported language
        if language_code and language_code in LANGUAGES:
            return session["language_code"]
        else:
            language_code = request.accept_languages.best_match(LANGUAGES)
            log.info(f"language_code best match set to: {language_code}")
            return request.accept_languages.best_match(LANGUAGES)

    Babel(app, locale_selector=get_locale)

    @app.before_request
    def start_session():
        session.permanent = True
        try:
            session["sid"]
        except KeyError:
            session["sid"] = urllib.parse.quote_plus(b64encode(os.urandom(10)))
            log.info(f"Starting with sid {session['sid']}")

    CORS(app)
    images = UploadSet("images", IMAGES)
    configure_uploads(app, images)

    from . import auth
    from . import views
    from . import api

    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)
    app.register_blueprint(api.api)
    from .blueprints.admin import admin
    from .blueprints.checkout import checkout
    from .blueprints.subscriber import subscriber
    from .blueprints.pages import module_pages
    from .blueprints.iframe import module_iframe_embed
    from .blueprints.style import module_style_shop
    from .blueprints.seo import module_seo_page_title
    from .blueprints.api import apiv1
    from .blueprints.document import document_blueprint

    app.register_blueprint(module_pages, url_prefix="/pages")
    app.register_blueprint(module_iframe_embed, url_prefix="/iframe")
    app.register_blueprint(module_style_shop, url_prefix="/style")
    app.register_blueprint(module_seo_page_title, url_prefix="/seo")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(checkout)
    app.register_blueprint(subscriber)
    app.register_blueprint(apiv1, url_prefix="/api/v1/")
    app.register_blueprint(document_blueprint)

    app.add_url_rule("/", "index", views.__getattribute__("choose"))

    with app.app_context():
        database.init_app(app)
        Migrate(app, database)

        """Migrate database when app first boots"""
        log.info("Migrating database")
        migrations_dir_context = files("migrations")
        # See:
        # https://importlib-resources.readthedocs.io/en/latest/using.html#using-importlib-resources
        # https://docs.python.org/3.11/library/importlib.resources.html#importlib.resources.as_file
        # https://docs.python.org/3/whatsnew/3.12.html#importlib-resources
        # https://bugs.python.org/issue45427
        # https://github.com/python/importlib_resources/pull/255
        with as_file(migrations_dir_context) as migrations_dir_tmp:
            log.info(f"migrations_dir_tmp is {migrations_dir_tmp}")
            log.info(
                "https://docs.python.org/3.11/library/importlib.resources.html#importlib.resources.as_file"  # noqa: E501
            )
            log.info("Performing database migration (if any)")
            upgrade(directory=migrations_dir_tmp)

        """Import any custom modules"""
        # Set custom modules path
        modulesPath = Path(app.config["MODULES_PATH"])
        if modulesPath.exists() is False:
            msg = f"Configured MODULES_PATH '{modulesPath}' does not exist"
            log.error(msg)
            abort(msg)

        sys.path.append(app.config["MODULES_PATH"])
        modules = Module.query.all()
        log.info(f"sys.path contains: {sys.path}")
        for module in modules:
            # Assume standard python module
            try:
                log.info(f"Attempting to importing module: {module.name}")
                importlib.import_module(module.name)
            except ModuleNotFoundError:
                log.debug(f"Error: Could not import module: {module.name}")
            # Register modules as blueprint (if it is one)
            try:
                importedModule = importlib.import_module(module.name)
                if isinstance(getattr(importedModule, module.name), Blueprint):
                    # Load any config the Blueprint declares
                    blueprint = getattr(importedModule, module.name)
                    blueprintConfig = "".join([blueprint.root_path, "/", "config.py"])
                    app.config.from_pyfile(blueprintConfig, silent=True)
                    # Register the Blueprint
                    app.register_blueprint(getattr(importedModule, module.name))
                    log.info(f"Imported {module.name} as flask Blueprint")

            except (ModuleNotFoundError, AttributeError):
                log.error(f"Error: Could not import module as blueprint: {module.name}")

        try:
            payment_provider = PaymentProvider.query.first()
            if payment_provider is None:
                # If payment provider table not seeded, seed with blank values.
                payment_provider = PaymentProvider()
                database.session.add(payment_provider)
                database.session.commit()
        except sqlalchemy.exc.OperationalError as e:
            # Allow to fail until migrations run (flask upgrade requires app reboot)
            log.debug(e)
        try:
            # Ensure shop has a PriceList for each supported currency
            # such PriceList contains zero rules so effectively returns the plan.sell_price # noqa: E501
            # and plan.interval_amount without any price adjustments.
            # Note that PriceLists must also be assigned to plan(s) to be in effect.
            price_lists = PriceList.query.all()
            # If there are zero PriceLists this may mean shop is outdated and
            # therefore needs its initial PriceLists created
            if len(price_lists) == 0:
                # Create default PriceList with zero rules for each supported currency
                for currency in settings.get("SUPPORTED_CURRENCIES"):
                    log.debug(
                        f"Creating PriceList with zero rules for currency {currency}"  # noqa: E501
                    )
                    price_list = PriceList(
                        currency=currency, name=f"Default {currency}"
                    )  # noqa: E501
                    database.session.add(price_list)
                    database.session.commit()
                    log.debug(
                        f"Created PriceList with zero rules for currency {currency}"
                    )
        except sqlalchemy.exc.OperationalError as e:
            # Allow to fail until migrations run (flask upgrade requires app reboot)
            log.debug(e)

        load_theme(app)

    # Handling Errors Gracefully
    @app.errorhandler(404)
    def page_not_found(e):
        log.debug(f"Route does not exist {request.url}")
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return "File Too Large", 413

    @app.errorhandler(500)
    def page_error_500(e):
        return render_template("errors/500.html"), 500

    @app.cli.command()
    def initdb():
        """Initialize the database."""
        click.echo("Init the db")
        DBseedFile = Path("seed.sql")
        if DBseedFile.exists() is False:
            log.warning(f"DBseedFile does not exist in {os.getcwd()}")
            DBseedFile = files("subscribie").parent.joinpath("seed.sql")
            log.warning(
                f"Attempting to load DBseedFile from package dir at {DBseedFile}"
            )
        with open(DBseedFile) as fp:
            con = sqlite3.connect(app.config["DB_FULL_PATH"])
            cur = con.cursor()
            # Check not already seeded
            cur.execute("SELECT id from user")
            if cur.fetchone() is None:
                cur.executescript(fp.read())
            else:
                log.info("Database already seeded.")
            con.close()
        # assignDefaultPriceLists to each plan
        plans = Plan.query.all()
        for plan in plans:
            plan.assignDefaultPriceLists()
        database.session.commit()

    @app.cli.command()
    @click.argument("days", type=int)
    def backfill_transactions(days):
        click.echo(f"Beginning transaction backfill for {days} days")
        call_backfill_transactions(days=days)

    @app.cli.command()
    @click.argument("days", type=int)
    def backfill_subscriptions(days):
        click.echo(f"Beginning subscription backfill for {days} days")
        call_backfill_subscriptions(days=days)

    @app.cli.command()
    @click.argument("days", type=int)
    def backfill_persons(days):
        click.echo(f"Beginning person backfill for {days} days")
        call_backfill_persons(days=days)

    @app.cli.command()
    @click.argument("days", type=int)
    def backfill_stripe_invoices(days):
        click.echo(f"Beginning stripe invoices backfill for {days} days")
        call_backfill_stripe_invoices(days=days)

    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    @translate.command()
    def update():
        """Update all languages."""
        if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
            raise RuntimeError("extract command failed")
        if os.system("pybabel update -i messages.pot -d subscribie/translations"):
            raise RuntimeError("update command failed")
        os.remove("messages.pot")

    @translate.command()
    def compile():
        """Compile all languages."""
        if os.system("pybabel compile -d subscribie/translations"):
            raise RuntimeError("compile command failed")

    @translate.command()
    @click.argument("lang")
    def init(lang):
        """Initialize a new language."""
        if os.system("pybabel extract -F babel.cfg -k _l -o messages.pot ."):
            raise RuntimeError("extract command failed")
        if os.system(
            "pybabel init -i messages.pot -d subscribie/translations -l " + lang
        ):
            raise RuntimeError("init command failed")
        os.remove("messages.pot")

    @app.cli.command()
    def alert_subscribers_make_choice():
        """Alert qualifying subscribers to set their choices

        For all people (aka Subscribers)

        - Loop over their *active* subscriptions
        - Check if x days before their subscription.next_date
        - If yes, sent them an email alert
        """

        def alert_subscriber_update_choices(subscriber: Person):
            email_template = str(
                Path(current_app.root_path + "/emails/update-choices.jinja2.html")
            )
            # App context needed for request.host (app.config["SERVER_NAME"] not set)
            with app.test_request_context("/"):
                update_options_url = (
                    "https://" + request.host + url_for("subscriber.login")
                )
                company = Company.query.first()
                with open(email_template) as file_:
                    template = Template(file_.read())
                    html = template.render(
                        update_options_url=update_options_url, company=company
                    )
                    try:
                        msg = EmailMessageQueue()
                        msg["Subject"] = company.name + " " + "Update Options"
                        msg["FROM"] = current_app.config["EMAIL_LOGIN_FROM"]
                        msg["To"] = person.email
                        msg.set_content(update_options_url)
                        msg.add_alternative(html, subtype="html")
                        msg.queue()
                    except Exception as e:
                        log.error(f"Failed to send update choices email. {e}")

        people = Person.query.all()

        for person in people:
            for subscription in person.subscriptions:
                if subscription.stripe_status == "active":
                    # Check if x days until next subscription due, make configurable
                    today = datetime.date.today()
                    days_until = subscription.next_date().date() - today
                    if days_until.days == 8:
                        log.info(
                            f"Sending alert for subscriber '{person.id}' on \
                              plan: {subscription.plan.title}"
                        )
                        alert_subscriber_update_choices(person)

    @app.route("/test-language")
    def test_language():
        return _("Hello")

    @app.route("/error")
    def raise_error():
        1 / 0  # raises an error
        return ""

    @app.route("/ui-error")
    def raise_ui_error():
        """Raises UI error"""
        return render_template("errors/ui-error.html"), 200

    return app
