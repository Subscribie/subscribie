# -*- coding: utf-8 -*-
"""                                                                              
    subscribie.app                                                                 
    ~~~~~~~~~                                                                    
    A microframework for buiding subsciption websites.                                                                                 
    This module implements the central subscribie application.              
                                                                                 
    :copyright: (c) 2018 by Karma Computing Ltd
"""
from os import path
import logging
from dotenv import load_dotenv

# Create logger
logger = logging
import os
from os import environ
import sys
import random
import requests
import time
import gocardless_pro
import sqlite3
import smtplib
from email.mime.text import MIMEText
import jinja2
import flask
import datetime
from base64 import b64encode, urlsafe_b64encode
import git
import shutil
from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    escape,
    request,
    current_app,
    send_from_directory,
    jsonify,
    Blueprint,
)
from oauth2client.client import OAuth2WebServerFlow
import yaml
from .forms import (
    StripWhitespaceForm,
    LoginForm,
    PasswordLoginForm,
    CustomerForm,
    GocardlessConnectForm,
    StripeConnectForm,
    TawkConnectForm,
    GoogleTagManagerConnectForm,
    PlansForm,
    ChangePasswordForm,
    ChangeEmailForm,
    AddShopAdminForm,
    SubscriberForgotPasswordForm,
    SubscriberResetPasswordForm,
    ForgotPasswordForm,
    ForgotPasswordResetPasswordForm,
    ChoiceGroupForm
)
from .Template import load_theme
from blinker import signal
from flask_cors import CORS
from flask_uploads import configure_uploads, UploadSet, IMAGES, patch_request_class
import importlib
from importlib import reload
import urllib
from pathlib import Path
import subprocess
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask_migrate import Migrate, upgrade
import click
from jinja2 import Template
from flask_mail import Mail, Message

database = SQLAlchemy()

from .models import (User, Person, Subscription, SubscriptionNote, Company, 
                    Page, Module, PaymentProvider, Integration, Plan,
                    PlanRequirements, PlanSellingPoints,
                    ChoiceGroup, Option)

from .blueprints.admin import get_subscription_status, create_stripe_webhook

def seed_db():                                                                 
    # Add module_seo_page_title    
    module_seo = Module()                                                        
    module_seo.name = 'module_seo_page_title'                                    
    module_seo.src = 'https://github.com/Subscribie/module-seo-page-title.git'   
    database.session.add(module_seo)
    module_pages = Module()
    module_pages.name = 'module_pages'
    module_pages.src = 'https://github.com/Subscribie/module-pages.git'                                                   
    database.session.commit()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    app.config.update(
     os.environ
    )

    if test_config is not None:
        app.config.update(
            test_config
        )

    if not os.path.exists(app.config["UPLOADED_FILES_DEST"]):
        print("Creating UPLOADED_FILES_DEST directory" + app.config["UPLOADED_FILES_DEST"])
        os.makedirs(app.config["UPLOADED_FILES_DEST"])

    @app.before_request
    def start_session():
        try:
            session["sid"]
        except KeyError:
            session["sid"] = urllib.parse.quote_plus(b64encode(os.urandom(10)))
            print("Starting with sid {}".format(session["sid"]))

    @app.before_first_request
    def register_custom_page_routes():
        """Register custom pages as routes"""
        pages = Page.query.all()
        for page in pages:
            page_path = page.path
            template_file = page.template_file
            view_func_name = page_path
            # Generate view function
            generate_view_func = """def %s_view_func():
            return render_template('%s', title="%s")""" % (
                view_func_name,
                template_file,
                page.page_name
            )
            exec(generate_view_func) in globals(), locals()
            method_name = view_func_name + "_view_func"
            possibles = globals().copy()
            possibles.update(locals())
            view_func = possibles.get(method_name)
            print(f"Attempting to add rule for page_path: {page_path}, view_func_name: {view_func_name}, view_func: {view_func}")
            for rule in app.url_map.iter_rules():
                if rule.rule == "/" + page_path:
                    print(f"Refusing to overwrite existing url rule for {page_path}")
                else:
                    app.add_url_rule("/" + page_path, view_func_name + "_view_func", view_func)

    @app.before_first_request
    def register_modules():
        """Import any custom modules"""
        # Set custom modules path
        sys.path.append(app.config["MODULES_PATH"])
        modules = Module.query.all()
        print("sys.path contains: {}".format(sys.path))
        for module in modules:
            # Assume standard python module
            try:
                print("Attempting to importing module: {}".format(module.name))
                importlib.import_module(module.name)
            except ModuleNotFoundError:
                # Attempt to load module from src 
                dest = Path(app.config["MODULES_PATH"], module.name)
                print("Cloning module into: {}".format(dest))
                os.makedirs(str(dest), exist_ok=True)
                try:
                    git.Repo.clone_from(module.src, dest)
                except git.exc.GitCommandError:
                    pass
                # Now re-try import
                try:
                    import site

                    reload(site)
                    importlib.import_module(module.name)
                except ModuleNotFoundError:
                    print("Error: Could not import module: {}".format(module.name))
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
                    print(f"Imported {module.name} as flask Blueprint")

            except (ModuleNotFoundError, AttributeError):
                print(
                    "Error: Could not import module as blueprint: {}".format(
                        module.name
                    )
                )


    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    images = UploadSet("images", IMAGES)
    patch_request_class(app, int(app.config.get('MAX_CONTENT_LENGTH', 2 * 1024 * 1024)))
    configure_uploads(app, images)

    from . import db
    from . import auth
    from . import views
    from . import api

    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)
    app.register_blueprint(api.api)
    from .blueprints.admin import admin
    from .blueprints.subscriber import subscriber
    from .blueprints.pages import module_pages
    from .blueprints.iframe import module_iframe_embed

    app.register_blueprint(module_pages, url_prefix="/pages")
    app.register_blueprint(module_iframe_embed, url_prefix="/iframe")
    app.register_blueprint(admin, url_prefix="/admin")
    app.register_blueprint(subscriber)

    app.add_url_rule("/", "index", views.__getattribute__("choose"))

    # the signals
    from .signals import journey_complete


    with app.app_context():

        database.init_app(app)
        migrate = Migrate(app, database)

        try:
            payment_provider = PaymentProvider.query.first()
            if payment_provider is None:
                # If payment provider table is not seeded, seed it now with blank values.
                payment_provider = PaymentProvider()
                database.session.add(payment_provider)
                database.session.commit()
                create_stripe_webhook()
        except sqlalchemy.exc.OperationalError as e:
            # Allow to fail until migrations have been ran (flask upgrade requires app boot)
            print(e)

        load_theme(app)

    # Handling Errors Gracefully
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        return 'File Too Large', 413

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("errors/500.html"), 500

    @app.cli.command()
    def initdb():
        """Initialize the database."""
        click.echo('Init the db')
        with open("seed.sql") as fp:
            con = sqlite3.connect(app.config["DB_FULL_PATH"])
            cur = con.cursor()
            cur.executescript(fp.read())
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
            email_template = str(Path(current_app.root_path + '/emails/update-choices.jinja2.html'))
            # App context needed for dynamic request.host (app.config["SERVER_NAME"] not set)
            with app.test_request_context('/'):
                update_options_url ='https://' + flask.request.host + url_for('subscriber.login')
                company = Company.query.first()
                with open(email_template) as file_:
                    template = Template(file_.read())
                    html = template.render(update_options_url=update_options_url,
                                            company=company)
                    try:
                        mail = Mail(current_app)
                        msg = Message()
                        msg.subject = company.name + " " + "Update Options"
                        msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
                        msg.recipients = [person.email]
                        msg.html = html
                        mail.send(msg)
                    except Exception as e:
                        print(e)
                        print("Failed to send update choices email")
                        
        people = Person.query.all()

        for person in people:
            for subscription in person.subscriptions:
                if get_subscription_status(subscription.gocardless_subscription_id) == "active":
                    # Check if x days until next subscription due, make configurable
                    today = datetime.date.today()
                    days_until = subscription.next_date().date() - today
                    if days_until.days == 8:
                        print(f"Sending alert for subscriber '{person.id}' on plan: {subscription.plan.title}")
                        alert_subscriber_update_choices(person)


    return app
