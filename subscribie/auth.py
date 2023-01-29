import logging
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
    Markup,
)
from subscribie.email import EmailMessageQueue
from subscribie.utils import get_stripe_secret_key, get_stripe_connect_account
from base64 import urlsafe_b64encode
import os
from .forms import (
    LoginForm,
    PasswordLoginForm,
    ForgotPasswordForm,
    ForgotPasswordResetPasswordForm,
)
from .models import database, User, Person, Company, Page, LoginToken, Setting
import binascii
from pathlib import Path
from jinja2 import Template
from flask import jsonify
import jwt
from py_auth_header_parser import parse_auth_header
import datetime
import stripe
from flask_babel import _

log = logging.getLogger(__name__)
bp = Blueprint("auth", __name__, url_prefix="/auth")


def saas_api_only(f):
    """Allow or deny requests if they providate a
    valid SAAS_API_KEY

    The SAAS_API_KEY api is used for Subscribie to
    communicate with shops created by the shop builder.
    For example, for activating/deactivating a shop,
    Subscribie can make an authenticated api request
    to a shop to activate or deactivate a shop when
    also providing a valid SAAS_API_KEY.
    """

    @functools.wraps(f)
    def wrapper(*args, **kwds):
        SAAS_API_KEY = current_app.config.get("SAAS_API_KEY")
        if request.args.get("SAAS_API_KEY") and SAAS_API_KEY == request.args.get(
            "SAAS_API_KEY"
        ):  # noqa: E501
            pass  # Authenticated, allow request

        if request.args.get("SAAS_API_KEY") is None:
            resp = jsonify({"error": "SAAS_API_KEY required"})
            return resp, 401
        if SAAS_API_KEY != request.args.get("SAAS_API_KEY"):

            resp = jsonify({"error": "Invalid SAAS_API_KEY"})

            return resp, 401
        return f(*args, **kwds)

    return wrapper


def token_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        if g.user is not None:
            log.debug(
                "Skipping token_required since g.user is not None and therefore cookie authenticated"  # noqa: E501
            )
            return f(*args, **kwds)
        if "Authorization" not in request.headers:
            resp = jsonify({"msg": "Not authenticated"})
            resp.headers.set("www-authenticate", "Bearer")
            log.debug(
                f"""Refusing login since Authorization not in request.headers.\n\n
                The headers were: '{request.headers}'"""
            )
            return resp, 401

        auth_header = parse_auth_header(request.headers["Authorization"])

        log.debug("Attemping api token authentication")
        settings = Setting.query.first()

        from subscribie.api import decrypt_secret

        api_key = decrypt_secret(settings.api_key_secret_test).decode("utf-8")
        if auth_header["access_token"] == api_key:
            log.debug("access_token matched api_key")
            assert api_key is not None
            assert api_key != ""
            log.debug("api_key was not None and was not empty")
            return f(*args, **kwds)

        log.warning("access_token did not match api_key")

        log.debug("Checking if jtw based auth used, about to Validate & decode jwt")
        public_key = open(current_app.config["PUBLIC_KEY"]).read()
        try:
            jwt.decode(auth_header["access_token"], public_key, algorithms=["RS256"])
            log.debug("jwt.decode was successful")
        except jwt.exceptions.InvalidSignatureError as e:
            log.exception(f"jwt.exceptions.InvalidSignatureError: {e}")
            return jsonify({"msg": "InvalidSignatureError"}), 401
        except jwt.exceptions.ExpiredSignatureError as e:
            log.exception(f"jwt.exceptions.ExpiredSignatureError: {e}")
            return jsonify({"msg": "ExpiredSignatureError"}), 401
        except jwt.exceptions.InvalidAlgorithmError as e:
            log.exception(f"jwt.exceptions.InvalidAlgorithmError: {e}")
            return jsonify({"msg": "InvalidAlgorithmError"}), 401
        except jwt.exceptions.DecodeError as e:
            log.exception(f"jwt.exceptions.DecodeError: {e}")
            return jsonify({"msg": "DecodeError"}), 401
        except Exception as e:
            log.exception(f"jwt general Exception: {e}")
            return jsonify({"msg": "Token could not be validated or was missing"})

        return f(*args, **kwds)

    return wrapper


def get_magic_login_link(email, password):
    login_url = generate_login_url(email)
    log.debug("In get_magic_login_link")
    if check_password_login(email, password):
        log.debug(
            f"get_magic_login_link->check_password_login OK. Returning login_url: {login_url}"  # noqa: E501
        )
        resp = {"login_url": login_url}
        return resp
    log.debug(f"get_magic_login_link->check_password_login failed for email {email}")
    raise


@bp.route("/jwt-login", methods=["GET", "POST"])
def jwt_login():
    log.debug("In jwt_login")
    if "Authorization" in request.headers:
        log.debug(
            "Authorization header present, so attempting to get email & password from Authorization header"  # noqa: E501
        )
        email = request.authorization.username
        password = request.authorization.password
        log.debug(f"Email in Authorization header was: {email}")
    elif (
        request.method == "POST"
        and request.headers.get("Content-Type") == "application/x-www-form-urlencoded"
    ):  # Oauth style login from form POST
        log.debug(
            "jwt_login was POST request & x-www-form-urlencoded so getting email & password from POST request"  # noqa: E501
        )
        email = request.form.get("username", "")
        password = request.form.get("password", "")
        log.debug(f"Email from POST x-www-form-urlencoded request was: {email}")
    elif (  # json post login
        request.method == "POST"
        and request.headers.get("Content-Type") == "application/json"
    ):
        log.debug("jwt_login was POST & application/json request")
        email = request.json["username"]
        password = request.json["password"]
        log.debug(f"Email from POST application/json request was: {email}")
    user = User.query.filter_by(email=email).first()
    if user is not None:
        log.debug("Successfully located user object during jwt_login")
        # Check password
        if not user.check_password(password):
            log.error(f"No password is set for {user.email}. Refusing to login")
            return jsonify({"msg": "Bad credentials"}), 401

        log.debug("Generating jwt token")
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
    else:
        log.error(
            f'Unable to locate user using email "{email}". Refusing to generate jtw token'  # noqa: E501
        )
    return jsonify({"msg": "Bad credentials"})


@bp.route("/protected")
@token_required
def protected():
    """Verify token based authentication"""
    log.debug("In /protected, to verify token based authentication.")
    return jsonify({"msg": "Success"})


def check_password_login(email, password):
    log.debug("In check_password_login")
    user = User.query.filter_by(email=email).first()
    if user.check_password(password):
        log.debug(
            f'user.check_password was successfull in check_password_login for email: "{email}"'  # noqa: E501
        )
        return True
    log.debug(
        f'user.check_password failed in check_password_login for email: "{email}"'
    )
    return False


def start_new_user_session(email):
    session.clear()
    log.debug(
        f"session cleared & new session started for email '{email}' in start_new_user_session"  # noqa: E501
    )
    session["user_id"] = email


@bp.route("/login", methods=["POST"])
def send_login_token_email():
    log.debug("In send_login_token_email")
    magic_login_form = LoginForm()
    password_login_form = PasswordLoginForm()

    if password_login_form.validate_on_submit():
        log.debug(
            "Form validation successfull for password_login_form.validate_on_submit"
        )
        email = password_login_form.data["email"]
        log.debug(f"Login email was: {email}")
        password = password_login_form.data["password"]
        user = User.query.filter_by(email=email).first()
        if user is None:
            msg = "Email address not found, did you sign-up with a different email address?"  # noqa: E501
            flash(msg)
            log.debug(f"{msg}. Email: {email}")
            return redirect(url_for("auth.login"))

        if check_password_login(email, password):
            log.debug(
                f"Successful form login for '{email}'. Redirecting to admin dashboard"
            )
            start_new_user_session(email)
            return redirect(url_for("admin.dashboard"))
        else:
            session.clear()
            log.debug(f'Invalid password during form login using email "{email}"')
            flash("Invalid password")
            log.debug(f'Redirecting user back to {url_for("auth.login")}')
            return redirect(url_for("auth.login"))

    if magic_login_form.validate_on_submit():
        log.debug("In magic_login_form.validate_on_submit")
        email = magic_login_form.data["email"]
        user = User.query.filter_by(email=email).first()
        if user is None:
            msg = "Email address not found, did you sign-up with a different email address?"  # noqa: E501
            flash(msg)
            log.debug(f"User not found during magic login. Email: '{email}'")
            log.debug(f'Redirecting user back to {url_for("auth.login")}')
            return redirect(url_for("auth.login"))
        try:
            log.debug(
                f'Attempting to send_login_url for {magic_login_form.data["email"]}'
            )
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
            log.debug("Asking user to check their email")
            return render_template_string(source)
        except Exception as e:
            log.error(f"Failed to generate login email. {e}")
            return "Failed to generate login email."

    # If reach here, then neither PasswordLoginForm nor magic_login_form have validated
    flash(
        _(
            "Please provide at least your email address to login, or use the forgot password feature."  # noqa: E501
        )
    )
    return redirect(url_for("auth.login"))


@bp.route("/login", methods=["GET"])
def login():
    log.debug("In login")
    if g.user is not None:
        log.debug(
            f'User is already logged in, redirecting to {url_for("admin.dashboard")}'
        )
        return redirect(url_for("admin.dashboard"))
    form = LoginForm()
    log.debug("Sending user to login form")
    return render_template("/admin/login.html", form=form)


@bp.route("/login/<login_token>", methods=("GET", "POST"))
def do_login(login_token):
    log.debug("In do_login for login_token based login")
    if len(login_token) < 10:
        log.debug("Invalid login_token length. Refusing to login.")
        return "Invalid token"

    # Try to get user from login_token
    user = User.query.filter_by(login_token=login_token).first()
    if user is not None:
        log.debug(f"Located user via login token on user table. Email: '{user.email}'")
        # Invalidate previous token
        new_login_token = urlsafe_b64encode(os.urandom(24))
        user.login_token = new_login_token
        database.session.commit()
    else:
        # Try and get token from LoginToken table
        # This user.login_token is for backward compatibility
        # LoginToken table is the prefered model to use.
        token = LoginToken.query.filter_by(login_token=login_token).first()
        log.debug(
            "Unable to locate login_token on user model, so attempting to locate valid login token via LoginToken table"  # noqa: E501
        )
        if token is not None:
            user = Person.query.filter_by(uuid=token.user_uuid).first()
            # Invalidate previous token
            database.session.delete(token)
            database.session.commit()

    if user is None:
        log.debug(
            "Unable to locate user via login_token for user.login_token nor LoginToken"
        )
        return "User not found"
    else:
        log.degbug(
            f"Successfully located user via valid login token. Email: {user.email}"
        )

    start_new_user_session(user.email)

    if isinstance(user, User):
        log.debug("Starting new session for shop owner by setting session['user_id']")
        session["user_id"] = user.email
        log.debug(f'Redirecting shop owner to: {url_for("admin.dashboard")}')
        return redirect(url_for("admin.dashboard"))
    elif isinstance(user, Person):
        log.debug(
            "Starting new session for subscriber by setting session['subscriber_id']"
        )
        session["subscriber_id"] = user.email
        log.debug(f'Redirecting subscriber to: {url_for("subscriber.account")}')
        return redirect(url_for("subscriber.account"))


@bp.before_app_request
def load_logged_in_user():
    log.debug("In load_logged_in_user")
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(email=user_id).first()
    log.debug(f"Set g.user to {g.user}")


def generate_login_token():
    log.debug("In generate_login_token")
    login_token = urlsafe_b64encode(os.urandom(24)).decode("utf-8")
    return login_token


def generate_login_url(email):
    """Generate login token url"""
    log.debug("In generate_login_url")
    login_token = generate_login_token()
    user = User.query.filter_by(email=email.lower()).first()

    if user is not None:
        user.login_token = login_token
        log.debug(f"The located user was: {user.email}")
    elif user is None:
        user = Person.query.filter_by(email=email.lower()).first()
        log.debug(f"The located person was: {user.email}")
        if user is not None:
            # Insert login token into db
            loginToken = LoginToken()
            loginToken.user_uuid = user.uuid
            loginToken.login_token = login_token
            database.session.add(loginToken)

    if user is None:
        log.debug(f"Unable to locate user for generate_login_url. Email: {email}")
        return "Invalid valid user"

    database.session.commit()
    login_url = "".join([request.host_url, "auth/login/", login_token])
    log.info(f"One-time login url: {login_url}")
    return login_url


def send_login_url(email):
    log.debug("In send_login_url")
    login_url = generate_login_url(email)
    html = """\
    <html>
        <head></head>
        <body>
        <p>Login to your Subscribie account using the link below:</p>
    """
    html = "".join([html, '<a href="', login_url, '">Login now</a>', "</body></html>"])
    log.info("Generated login url: %s", login_url)
    log.info("Sending login email to: %s", email)
    msg = EmailMessageQueue()
    subject = "Subscribie Magic Login"
    msg["Subject"] = subject
    msg["FROM"] = current_app.config["EMAIL_LOGIN_FROM"]
    msg["To"] = email
    msg.set_content = login_url
    msg.add_alternative(html, subtype="html")
    msg.queue()
    log.debug(
        f"Added magic login url email to queue. To: '{email}'. Subject: '{subject}'"
    )


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    log.debug("In forgot_password")
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.data["email"]
        log.debug(f"Form validated for ForgotPasswordForm. Email: '{email}'")
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash("User not found with that email")
            log.debug(
                f"User not found for {email}. Refusing to send forgot password email"
            )
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
            "https://" + request.host + "/auth/password-reset?token=" + token
        )
        log.info(f"password_reset_url: {password_reset_url}")

        with open(email_template) as file_:
            template = Template(file_.read())
            html = template.render(
                password_reset_url=password_reset_url, company=company
            )

            try:
                msg = EmailMessageQueue()
                msg["Subject"] = company.name + " " + "Password Reset"
                msg["From"] = current_app.config["EMAIL_LOGIN_FROM"]
                msg["To"] = email
                msg.set_content(password_reset_url)
                msg.add_alternative(html, subtype="html")
                msg.queue()
            except Exception as e:
                log.error(f"Failed to send user password reset email. {e}")
            flash(
                "We've sent you an email with a password reset link, \
                please check your spam/junk folder too"
            )

    return render_template("admin/forgot_password.html", form=form)


@bp.route("/password-reset", methods=["GET", "POST"])
def password_reset():
    "Perform password reset from email link, verify token"
    log.debug("In password_reset")
    form = ForgotPasswordResetPasswordForm()

    if form.validate_on_submit():
        if (
            User.query.filter_by(password_reset_string=form.data["token"]).first()
            is None
        ):
            log.debug("User not found using password reset token.")
            return "Invalid reset token"

        user = User.query.filter_by(password_reset_string=form.data["token"]).first()
        log.debug(f"User found using password reset token. Email: '{user.email}'")
        user.set_password(form.data["password"])
        database.session.commit()
        flash("Your password has been reset")
        log.debug(f"User password has been reset for user '{user.email}'")
        return redirect(url_for("auth.login"))

    if (
        request.args.get("token", None) is None
        or len(request.args["token"]) != 64
        or User.query.filter_by(password_reset_string=request.args["token"]).first()
        is None
    ):
        msg = "Invalid reset link. Please try generating a new reset link."
        log.debug(f"{msg}")
        return msg

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


def stripe_connect_id_required(view):
    """Redirect away from route if requires a Stripe Connect id

    NOTE:
    - Does *not* require Stripe Connect process is completed
    - Does require that a Stripe Connect id has been generated
    - e.g. The shop owner may have started the process but not yet
           finished Stripe onboarding


    Used to redirect views when Stripe Connect is required
    but there is a request to visit a page which needs Stripe
    connect to be completed.
    """

    log.debug("In stripe_connect_id_required")

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        stripe.api_key = get_stripe_secret_key()
        connect_account = get_stripe_connect_account()
        if connect_account is None:
            stripe_connect_url = url_for("admin.stripe_connect")
            flash(
                Markup(
                    f"You must <a href='{ stripe_connect_url }'>connect Stripe first.</a>"  # noqa: E501
                )
            )
            log.debug(f'Redirecting user to {url_for("admin.dashboard")}')
            return redirect(url_for("admin.dashboard"))

        return view(**kwargs)

    return wrapped_view


def protected_download(view):
    """Only allow authenticated users to download (Shop owners or subscribers)"""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is not None or g.subscriber is not None:
            log.debug("Allowing access to protected_download")
            return view(**kwargs)
        else:
            log.debug("Denying access to protected_download")
            return "Access denied", 401

    return wrapped_view


@bp.route("/logout")
def logout():
    session.clear()
    log.debug("/logout called")
    return render_template("admin/logout.html")


def check_private_page(page_id):
    """Block access to page if private, only allow shop owner or subscriber"""
    log.debug("In check_private_page")
    blocked = False
    page = Page.query.get(page_id)
    if page.private:
        if g.user is None and g.subscriber is None:
            blocked = True
            log.debug(f"Denying access to private page. page_id: {page_id}")
            return blocked, redirect("/")
    log.debug(f"Allowing access to page. page_id: {page_id}")
    return blocked, None
