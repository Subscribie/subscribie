import functools

from flask import (
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
from base64 import urlsafe_b64encode
import os
from .forms import (
    LoginForm,
    PasswordLoginForm,
    ForgotPasswordForm,
    ForgotPasswordResetPasswordForm,
)
from flask_mail import Mail, Message
from .models import database, User, Person, Company, Page, LoginToken
import binascii
from pathlib import Path
import flask
from jinja2 import Template
from flask import jsonify
import jwt
from functools import wraps
from py_auth_header_parser import parse_auth_header
import datetime
import logging

logger = logging

bp = Blueprint("auth", __name__, url_prefix="/auth")


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        # Skip token_required is user is cookie authenticated
        if g.user is not None:
            return f(*args, **kwds)
        if "Authorization" not in request.headers:
            resp = jsonify({"msg": "Not authenticated"})
            resp.headers.set("www-authenticate", "Bearer")

            return resp, 401

        auth_header = parse_auth_header(request.headers["Authorization"])
        # Validate & decode jwt
        public_key = open(current_app.config["PUBLIC_KEY"]).read()
        try:
            jwt.decode(auth_header["access_token"], public_key, algorithms=["RS256"])
        except jwt.exceptions.InvalidSignatureError:
            return jsonify({"msg": "InvalidSignatureError"}), 401
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({"msg": "ExpiredSignatureError"}), 401
        except jwt.exceptions.InvalidAlgorithmError:
            return jsonify({"msg": "InvalidAlgorithmError"}), 401
        except jwt.exceptions.DecodeError:
            return jsonify({"msg": "DecodeError"}), 401
        except Exception:
            return jsonify({"msg": "Token could not be validated or was missing"})

        return f(*args, **kwds)

    return wrapper


@bp.route("/jwt-login", methods=["GET", "POST"])
def jwt_login():

    if "Authorization" in request.headers:
        email = request.authorization.username
        password = request.authorization.password
    elif (
        request.method == "POST"
        and request.headers.get("Content-Type") == "application/x-www-form-urlencoded"
    ):  # Oauth style login from form POST
        email = request.form.get("username", "")
        password = request.form.get("password", "")
    elif (  # json post login
        request.method == "POST"
        and request.headers.get("Content-Type") == "application/json"
    ):
        email = request.json["username"]
        password = request.json["password"]
    user = User.query.filter_by(email=email).first()
    if user is not None:
        # Check password
        if not user.check_password(password):
            return jsonify({"msg": "Bad credentials"}), 401

        private_key = open(current_app.config["PRIVATE_KEY"]).read()
        jwt_payload = jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
                "user_id": user.id,
            },
            private_key,
            algorithm="RS256",
        )
        return jsonify({"token": jwt_payload})
    return jsonify({"msg": "Bad credentials"})


@bp.route("/protected")
@token_required
def protected():
    """Verify token based authentication"""
    return jsonify({"msg": "Success"})


def check_password_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user.check_password(password):
        return True
    return False


def start_new_user_session(email):
    session.clear()
    session["user_id"] = email


def oauth_login_user(email):
    """Log user in based on email address
    email must only be provided after a valid oauth
    flow completion"""
    user = User.query.filter_by(email=email).first()
    if user is not None:
        return True
    return False


@bp.route("/login", methods=["POST"])
def generate_login_token():
    magic_login_form = LoginForm()
    password_login_form = PasswordLoginForm()

    if password_login_form.validate_on_submit():
        email = password_login_form.data["email"]
        password = password_login_form.data["password"]
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("User not found with that email")
            return redirect(url_for("auth.login"))

        if check_password_login(email, password):
            start_new_user_session(email)
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
    if user is not None:
        # Invalidate previous token
        new_login_token = urlsafe_b64encode(os.urandom(24))
        user.login_token = new_login_token
        database.session.commit()
    else:
        # Try and get token from LoginToken table
        token = LoginToken.query.filter_by(login_token=login_token).first()
        if token is not None:
            user = Person.query.filter_by(uuid=token.user_uuid).first()
            # Invalidate previous token
            database.session.delete(token)
            database.session.commit()

    if user is None:
        return "Invalid valid user"

    start_new_user_session(user.email)

    if isinstance(user, User):
        session["user_id"] = user.email
        return redirect(url_for("admin.dashboard"))
    elif isinstance(user, Person):
        session["subscriber_id"] = user.email
        return redirect(url_for("subscriber.account"))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(email=user_id).first()


def generate_login_url(email):
    # Generate login token
    login_token = urlsafe_b64encode(os.urandom(24)).decode("utf-8")
    user = User.query.filter_by(email=email.lower()).first()

    if user is not None:
        user.login_token = login_token
    elif user is None:
        user = Person.query.filter_by(email=email.lower()).first()
        if user is not None:
            # Insert login token into db
            loginToken = LoginToken()
            loginToken.user_uuid = user.uuid
            loginToken.login_token = login_token
            database.session.add(loginToken)

    if user is None:
        return "Invalid valid user"

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


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.data["email"]
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("User not found with that email")
            return redirect(url_for("auth.forgot_password"))
        # Generate password reset token
        token = binascii.hexlify(os.urandom(32)).decode()
        user.password_reset_string = token
        database.session.commit()

        email_template = str(
            Path(current_app.root_path + "/emails/user-reset-password.jinja2.html")
        )
        company = Company.query.first()
        password_reset_url = (
            "https://" + flask.request.host + "/auth/password-reset?token=" + token
        )
        print(f"password_reset_url: {password_reset_url}")

        with open(email_template) as file_:
            template = Template(file_.read())
            html = template.render(
                password_reset_url=password_reset_url, company=company
            )

            try:
                mail = Mail(current_app)
                msg = Message()
                msg.subject = company.name + " " + "Password Reset"
                msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
                msg.recipients = [email]
                msg.html = html
                mail.send(msg)
            except Exception as e:
                print(e)
                print("Failed to send user password reset email")
            flash(
                "We've sent you an email with a password reset link, \
                please check your spam/junk folder too"
            )

    return render_template("admin/forgot_password.html", form=form)


@bp.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    "Perform password reset from email link, verify token"
    form = ForgotPasswordResetPasswordForm()

    if form.validate_on_submit():
        if (
            User.query.filter_by(password_reset_string=form.data["token"]).first()
            is None
        ):
            return "Invalid reset token"

        user = User.query.filter_by(password_reset_string=form.data["token"]).first()
        user.set_password(form.data["password"])
        database.session.commit()
        flash("Your password has been reset")
        return redirect(url_for("auth.login"))

    if (
        request.args.get("token", None) is None
        or len(request.args["token"]) != 64
        or User.query.filter_by(password_reset_string=request.args["token"]).first()
        is None
    ):
        return "Invalid reset link. Please try generating a new reset link."

    return render_template(
        "/admin/reset_password.html", token=request.args["token"], form=form
    )


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def protected_download(view):
    """Only allow authenticated users to download (Shop owners or subscribers)"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None or g.subscriber is not None:
            return view(**kwargs)
        else:
            return "Access denied", 401

    return wrapped_view


@bp.route("/logout")
def logout():
    session.clear()
    return render_template("admin/logout.html")


def check_private_page(page_id):
    """Block access to page if private, only allow shop owner or subscriber"""
    blocked = False
    page = Page.query.get(page_id)
    if page.private:
        if g.user is None and g.subscriber is None:
            blocked = True
            return blocked, redirect("/")
    return blocked, None
