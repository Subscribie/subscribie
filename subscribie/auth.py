import functools

from flask import (
    Flask,
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
    render_template_string,
)
from werkzeug.security import check_password_hash, generate_password_hash
from subscribie.db import get_db
from subscribie import logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from base64 import b64encode, urlsafe_b64encode
import smtplib
import sqlite3
import os
from .forms import LoginForm, PasswordLoginForm
from flask_mail import Mail, Message
from .models import database, User

bp = Blueprint("auth", __name__, url_prefix="/auth")


def check_password_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user.check_password(password):
        return True
    return False


@bp.route("/login", methods=["POST"])
def generate_login_token():
    magic_login_form = LoginForm()
    password_login_form = PasswordLoginForm()

    if password_login_form.validate_on_submit():
        email = password_login_form.data['email']
        password = password_login_form.data['password']
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("User not found with that email")
            return redirect(url_for("auth.login"))

        if check_password_login(email, password):
            session.clear()
            session["user_id"] = user.email
            return redirect(url_for("admin.dashboard"))
        else:
            session.clear()
            flash("Invalid password")
            return redirect(url_for("auth.login"))

    if magic_login_form.validate_on_submit():
        try:
            send_login_url(magic_login_form.data["email"])
            source = ' \
                {% extends "admin/layout.html" %} \
                {% block title %} Check your email {% endblock title %} \
                {% block body %} \
                 <div class="container"> \
                  <h1 class="display-2">Great.</h1> \
                  <h2>Now check your email.</h2> \
                  <p class="lead">We\'ve just sent you a login link.</p> \
                 </div> \
                {% endblock body %} '
            return render_template_string(source)
        except Exception as e:
            logger.error(e)
            logger.error("Failed to generate login email.")
            return "Failed to generate login email."


@bp.route("/login", methods=["GET"])
def login():
    form = LoginForm()
    return render_template("/admin/login.html", form=form)


@bp.route("/login/<login_token>", methods=("GET", "POST"))
def do_login(login_token):
    if len(login_token) < 10:
        return "Invalid token"
    # Try to get user from login_token
    user = User.query.filter_by(login_token=login_token).first()
    if user is None:
        return "Invalid valid user"

    session.clear()
    session["user_id"] = user.email
    
    # Invalidate previous token
    new_login_token = urlsafe_b64encode(os.urandom(24))
    user.login_token = new_login_token
    database.session.commit()
    return redirect(url_for("admin.dashboard"))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(email=user_id).first()


def generate_login_url(email):
    user = User.query.filter_by(email=email.lower()).first()
    if user is None:
        return "Invalid valid user"
    # Generate login token
    login_token = urlsafe_b64encode(os.urandom(24)).decode("utf-8")
    # Insert login token into db
    user.login_token = login_token
    database.session.commit()
    login_url = "".join([request.host_url, "auth/login/", login_token])
    print("One-time login url: {}".format(login_url))
    return login_url


def send_login_url(email):
    login_url = generate_login_url(email)
    html = """\
    <html>
        <head></head>
        <body>
        <p>Login to your Subscribie account using the link below:</p>
    """
    html = "".join([html, '<a href="', login_url, '">Login now</a>', "</body></html>"])
    logger.info("Generated login url: %s", login_url)
    logger.info("Sending login email to: %s", email)
    mail = Mail(current_app)
    msg = Message("Subscribie Magic Login")
    msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
    msg.recipients = [email]
    msg.body = login_url
    msg.html = html
    # Send email with token link
    mail.send(msg)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.route("/logout")
def logout():
    session.clear()
    return "Logged out"
