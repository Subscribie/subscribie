# -*- coding: utf-8 -*-                                                          
"""                                                                              
    subscribie.app                                                                 
    ~~~~~~~~~                                                                    
    A microframework for buiding subsciption websites.                                                                                 
    This module implements the central subscribie application.              
                                                                                 
    :copyright: (c) 2018 by Karma Crew                                           
"""
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
import flask_login
import datetime
from base64 import b64encode, urlsafe_b64encode
try:
    import sendgrid
    from sendgrid.helpers.mail import *
except Exception:
    pass
from flask import (Flask, render_template, session, redirect, url_for, escape, 
                   request, current_app, send_from_directory, jsonify)
from penguin_rest import Decorators
from penguin_rest import Rest
from oauth2client.client import OAuth2WebServerFlow
import yaml
from .jamla import Jamla
from .User import User, send_login_url, generate_login_url
from .forms import (StripWhitespaceForm, LoginForm, CustomerForm, 
                    GocardlessConnectForm, StripeConnectForm, ItemsForm)
from .Template import load_theme
from blinker import signal
from .cli import cli, run

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

app = Flask(__name__)                                                            
app.config['DEBUG'] = True
try:
    app.config.from_pyfile(os.environ['SUBSCRIBIE_ENV'])
except (KeyError, IOError):
    pass
try:
    cwd = os.getcwd()
    app.config.from_pyfile(cwd + '/.env')
except IOError:
    pass
app.secret_key = app.config['SECRET_KEY']                                           
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024                                 
alphanum = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRTUVWXYZ0123456789"
import  subscribie.views

jamlaApp = Jamla()                                                               
jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])

# Set custom modules path
sys.path.append(jamla['modules_path'])

load_theme(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
# Mock database
users = {'foo@bar.tld': {'password':'secret'}}

def hello():
    print "Hello"
    return True

@login_manager.user_loader
def user_loader(email):
    con = sqlite3.connect(app.config["DB_FULL_PATH"])
    con.row_factory = sqlite3.Row # Dict based result set
    cur = con.cursor()
    cur.execute('SELECT email FROM user WHERE email=?', (str(email),))
    result = cur.fetchone()
    con.close()
    if result is None:
        return
    user = User()
    user.id = email
    return user

@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return
    user = User()
    user.id = email

    user.is_authenticated = request.form['password'] == users['email']['password']
    return user

# Register yml pages as routes
if 'pages' in jamla:
    for i,v in enumerate(jamla['pages']):
        path = jamla['pages'][i][jamla['pages'][i].keys()[0]]['path']
        template_file = jamla['pages'][i][jamla['pages'][i].keys()[0]]['template_file']
        view_func_name = jamla['pages'][i].keys()[0]
        ##Generate view function
        generate_view_func = """def %s_view_func():
        return render_template('%s', jamla=jamla)""" % (view_func_name, template_file)
        exec(generate_view_func)
        method_name = view_func_name + "_view_func"
        possibles = globals().copy()
        possibles.update(locals())
        view_func = possibles.get(method_name)
        app.add_url_rule("/" + path, view_func_name + '_view_func', view_func)

# Handling Errors Gracefully

@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404
@app.errorhandler(500)
def page_not_found(e):
    return render_template('errors/500.html'), 500

# Import any custom modules
if 'modules' in jamla:
    try:
        for moduleName in jamla['modules']:
            print "Importing module: " + moduleName
            __import__(moduleName)
    except TypeError as e:
        print e


application = app
