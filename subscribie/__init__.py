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
    ItemsForm,
    ChangePasswordForm,
    ChangeEmailForm,
    AddShopAdminForm,
    SubscriberForgotPasswordForm,
    SubscriberResetPasswordForm,
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
from flask_migrate import Migrate, upgrade
import click

database = SQLAlchemy()

from .models import (User, Person, Subscription, SubscriptionNote, Company, 
                    Page, Module, PaymentProvider, Integration, Item,
                    ItemRequirements, ItemSellingPoints)

def seed_db():                                                                 
    # Add module_seo_page_title                                                  
    module_seo = Module()                                                        
    module_seo.name = 'module_seo_page_title'                                    
    module_seo.src = 'https://github.com/Subscribie/module-seo-page-title.git'   
    database.session.add(module_seo)                                                   
    database.session.commit()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    app.config.update(
     os.environ
    )

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
            view_func_name = page.page_name
            # Generate view function
            generate_view_func = """def %s_view_func():
            return render_template('%s')""" % (
                view_func_name,
                template_file,
            )
            exec(generate_view_func) in globals(), locals()
            method_name = view_func_name + "_view_func"
            possibles = globals().copy()
            possibles.update(locals())
            view_func = possibles.get(method_name)
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
                    print("Imported as flask Blueprint")
                    # Run Blueprint migrations if any
                    modulePath = Path(importedModule.__file__).parents[0]
                    moduleMigrationsPath = Path(modulePath, 'migrations')
                    if moduleMigrationsPath.is_dir():
                      # Run migrations
                      for migration in moduleMigrationsPath.iterdir():
                        print("Running module migration {}".format(migration))
                        # Run subscribie_cli database migrations
                        db_full_path = app.config['DB_FULL_PATH']
                        subprocess.call("python " + str(migration) + ' -up -db ' + db_full_path, shell=True)

            except (ModuleNotFoundError, AttributeError):
                print(
                    "Error: Could not import module as blueprint: {}".format(
                        module.name
                    )
                )


    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    images = UploadSet("images", IMAGES)
    patch_request_class(app, 2 * 1024 * 1024)
    configure_uploads(app, images)

    from . import db
    from . import auth
    from . import views

    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)
    from .blueprints.admin import admin_theme
    from .blueprints.subscriber import subscriber

    app.register_blueprint(admin_theme, url_prefix="/admin")
    app.register_blueprint(subscriber)

    app.add_url_rule("/", "index", views.__getattribute__("choose"))

    # the signals
    from .signals import journey_complete


    with app.app_context():

        database.init_app(app)
        migrate = Migrate(app, database)

        if test_config is not None:
            seed_db()
            app.config.update(
                test_config
            )

        load_theme(app)

    # Handling Errors Gracefully
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

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

    return app
