# -*- coding: utf-8 -*-
"""
    subscribie.app
    ~~~~~~~~~
    A microframework for buiding subsciption websites.
    This module implements the central subscribie application.

    :copyright: (c) 2018 by Karma Computing Ltd
"""
from dotenv import load_dotenv

from .logger import logger  # noqa: F401
import logging
import os
import sys
import sqlite3
from .database import database
import datetime
from base64 import b64encode
from flask import (
    Flask,
    render_template,
    session,
    url_for,
    current_app,
    Blueprint,
    request,
)
from subscribie.email import EmailMessageQueue
from .Template import load_theme
from flask_cors import CORS
from flask_uploads import (
    configure_uploads,
    UploadSet,
    IMAGES,
    patch_request_class,
)  # noqa: E501
import importlib
import urllib
from pathlib import Path
import sqlalchemy
from flask_migrate import Migrate
import click
from jinja2 import Template

from .models import PaymentProvider, Person, Company, Module, Plan, PriceList

load_dotenv(verbose=True)

log = logging.getLogger(__name__)


def seed_db():
    pass


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv(verbose=True)
    app.config.update(os.environ)

    if test_config is not None:
        app.config.update(test_config)

    @app.before_request
    def start_session():
        try:
            session["sid"]
        except KeyError:
            session["sid"] = urllib.parse.quote_plus(b64encode(os.urandom(10)))
            log.info(f"Starting with sid {session['sid']}")

    @app.before_first_request
    def register_modules():
        """Import any custom modules"""
        # Set custom modules path
        sys.path.append(app.config["MODULES_PATH"])
        modules = Module.query.all()
        log.info(f"sys.path contains: {sys.path}")
        for module in modules:
            # Assume standard python module
            try:
                log.info("Attempting to importing module: {module.name}")
                importlib.import_module(module.name)
            except ModuleNotFoundError:
                log.debug("Error: Could not import module: {module.name}")
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
                log.debug("Error: Could not import module as blueprint: {module.name}")

    CORS(app)
    images = UploadSet("images", IMAGES)
    patch_request_class(app, int(app.config.get("MAX_CONTENT_LENGTH", 2 * 1024 * 1024)))
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

    app.register_blueprint(module_pages, url_prefix="/pages")
    app.register_blueprint(module_iframe_embed, url_prefix="/iframe")
    app.register_blueprint(module_style_shop, url_prefix="/style")
    app.register_blueprint(module_seo_page_title, url_prefix="/seo")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(checkout)
    app.register_blueprint(subscriber)
    app.register_blueprint(apiv1, url_prefix="/api/v1/")

    app.add_url_rule("/", "index", views.__getattribute__("choose"))

    with app.app_context():

        database.init_app(app)
        Migrate(app, database)

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
            # therefore needs its inital PriceLists created
            if len(price_lists) == 0:
                # Create defaul PriceList with zero rules for each suported currency
                if os.getenv("SUPPORTED_CURRENCIES", False) is not False:
                    for currency in os.getenv("SUPPORTED_CURRENCIES").split(","):
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
                else:
                    log.debug("SUPPORTED_CURRENCIES is not set")
            # Ensure every plan has a PriceList attached for each supported currency
            plans = Plan.query.all()
            price_lists = (
                PriceList.query.all()
            )  # TODO only get default pricelist for given currency
            # since there is danger here that newly created pricelists may be added # noqa: E501
            for plan in plans:
                # Note we are careful to skip plans which already have a PriceList attached # noqa: E501
                # to handle the case of an already updated shop.
                if len(plan.price_lists) == 0:
                    for price_list in price_lists:
                        log.debug(
                            f"Adding price_list {price_list.name} to {plan.title}"
                        )
                        plan.price_lists.append(price_list)
                        database.session.commit()
                        log.debug(f"Added price_list {price_list.name} to {plan.title}")
        except sqlalchemy.exc.OperationalError as e:
            # Allow to fail until migrations run (flask upgrade requires app reboot)
            log.debug(e)

        load_theme(app)

    # Handling Errors Gracefully
    @app.errorhandler(404)
    def page_not_found(e):
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
        with open("seed.sql") as fp:
            con = sqlite3.connect(app.config["DB_FULL_PATH"])
            cur = con.cursor()
            # Check not already seeded
            cur.execute("SELECT id from user")
            if cur.fetchone() is None:
                cur.executescript(fp.read())
            else:
                log.info("Database already seeded.")
            con.close()

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

    return app
