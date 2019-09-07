# -*- coding: utf-8 -*-
"""                                                                              
    subscribie.app                                                                 
    ~~~~~~~~~                                                                    
    A microframework for buiding subsciption websites.                                                                                 
    This module implements the central subscribie application.              
                                                                                 
    :copyright: (c) 2018 by Karma Computing Ltd
"""
from .default_config import DefaultConfig
from os import path
import logging

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
from .bootstrap import bootstrap
from .jamla import Jamla
from .forms import (
    StripWhitespaceForm,
    LoginForm,
    CustomerForm,
    GocardlessConnectForm,
    StripeConnectForm,
    TawkConnectForm,
    GoogleTagManagerConnectForm,
    ItemsForm,
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


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    bootstrap(app)
    app.config.from_mapping(
        SECRET_KEY="dev", DATABASE=os.path.join(app.instance_path, "subscribie.sqlite")
    )
    # Overide config using /subscribie/volume/config.py if present
    # Only exists if inside kubernetes cluster
    if os.path.exists("/subscribie/volume/config.py"):
        print("Overiding config from /subscribie/volume/config.py")
        app.config.from_pyfile("/subscribie/volume/config.py", silent=True)
        print("The config is now:")
        for config in app.config:
            print(
                "{configName}:{configValue}".format(
                    configName=config, configValue=app.config[config]
                )
            )
    else:
        try:
            print("Falling back to default config.py within instance folder")
            app.config.from_pyfile("config.py", silent=False)
        except FileNotFoundError:
            print("Could not find default config, loading from default object")
            app.config.from_object(DefaultConfig)

    @app.before_request
    def start_session():
        try:
            session["sid"]
        except KeyError:
            session["sid"] = urllib.parse.quote_plus(b64encode(os.urandom(10)))
            print("Starting with sid {}".format(session["sid"]))

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    jamlaApp = Jamla()
    global jamla
    jamla = jamlaApp.load(src=app.config["JAMLA_PATH"])
    images = UploadSet("images", IMAGES)
    patch_request_class(app, 2 * 1024 * 1024)
    configure_uploads(app, images)

    from . import db

    db.init_app(app)
    from . import auth
    from . import views

    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)
    from .blueprints.admin import admin_theme

    app.register_blueprint(admin_theme, url_prefix="/admin")
    try:
        front_page = jamla["front_page"]
    except:
        front_page = "choose"
    try:
        app.add_url_rule("/", "index", views.__getattribute__(front_page))
    except AttributeError:
        app.add_url_rule("/", "index", views.__getattribute__("choose"))

    """The Subscribie object implements a flask application suited to subscription 
    based web applications and acts as the central object. Once it is created    
    it will act as a central registry for default views, application workflow,   
    the URL rules, and much more. Note most of the application must be defined   
    in Jamla format, a yaml based application markup.                            
                                                                                 
    Usually you create a :class:`Subscribie` instance in your main module or          
    in the :file:`__init__.py` file of your package like this::                  
                                                                                 
        from subscribie import Subscribie 
        app = Subscribie(__name__)                                                 
                                                                                 
    """
    # the signals
    from .signals import journey_complete

    alphanum = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRTUVWXYZ0123456789"

    # Set custom modules path
    if type(jamla["modules_path"]) is str:
        print("Setting module path to: {}".format(jamla["modules_path"]))
        sys.path.append(jamla["modules_path"])
    elif type(jamla["modules_path"]) is list:
        for path in jamla["modules_path"]:
            sys.path.append(path)

    with app.app_context():
        load_theme(app)

    # Register yml pages as routes
    if "pages" in jamla:
        for i, v in enumerate(jamla["pages"]):
            page = jamla["pages"][i].popitem()
            page_path = page[1]["path"]
            template_file = page[1]["template_file"]
            view_func_name = page[0]
            ##Generate view function
            generate_view_func = """def %s_view_func():
            return render_template('%s', jamla=jamla)""" % (
                view_func_name,
                template_file,
            )
            exec(generate_view_func) in globals(), locals()
            method_name = view_func_name + "_view_func"
            possibles = globals().copy()
            possibles.update(locals())
            view_func = possibles.get(method_name)
            app.add_url_rule("/" + page_path, view_func_name + "_view_func", view_func)

    # Handling Errors Gracefully
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("errors/500.html"), 500

    # Import any custom modules
    if "modules" in jamla:
        print("sys.path contains: {}".format(sys.path))
        for module in jamla["modules"]:
            # Assume standard python module
            try:
                print("Attempting to importing module: {}".format(module["name"]))
                importlib.import_module(module["name"])
            except ModuleNotFoundError:
                # Attempt to load module from src
                dest = jamla["modules_path"] + module["name"]
                print("Cloning module into: {}".format(dest))
                os.makedirs(dest, exist_ok=True)
                try:
                    git.Repo.clone_from(module["src"], dest)
                except git.exc.GitCommandError:
                    pass
                # Now re-try import
                try:
                    import site

                    reload(site)
                    importlib.import_module(module["name"])
                except ModuleNotFoundError:
                    print("Error: Could not import module: {}".format(module["name"]))
            # Register modules as blueprint (if it is one)
            try:
                importedModule = importlib.import_module(module["name"])
                if isinstance(getattr(importedModule, module["name"]), Blueprint):
                    # Load any config the Blueprint declares
                    blueprint = getattr(importedModule, module["name"])
                    blueprintConfig = "".join([blueprint.root_path, "/", "config.py"])
                    app.config.from_pyfile(blueprintConfig, silent=True)
                    # Register the Blueprint
                    app.register_blueprint(getattr(importedModule, module["name"]))
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
                        module["name"]
                    )
                )
    else:
        print("No modules element on jamla. Not loading any modules")
    return app
