from subscribie.auth import check_private_page, oauth_login_user, start_new_user_session
from pathlib import Path
import jinja2
import os
from jinja2 import Environment, FileSystemLoader
from flask import (
    abort,
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
    g,
    send_from_directory,
)
from .models import Company, Plan, Integration, Page, Category
from flask_migrate import upgrade
from subscribie.blueprints.style import inject_custom_style
import requests

bp = Blueprint("views", __name__, url_prefix=None)


@bp.before_app_first_request
def migrate_database():
    """Migrate database when app first boots"""
    print("#" * 233)
    upgrade(
        directory=Path(current_app.config["SUBSCRIBIE_REPO_DIRECTORY"] + "/migrations")
    )


@bp.before_app_request
def check_if_inside_iframe():
    """Set iframe_embeded in session object if app is loaded from inside an iframe
    If visited directly, (e.g. as a shop admin),
    then referer header is emtpy, and therefore the header/footer is
    displayed as normal.
    """
    if (
        request.args.get("iframe_embeded", False)
        or session.get("iframe_embeded") is True
        and request.headers.get("referer") is not None
    ):
        print("Loading from within iframe")
        session["iframe_embeded"] = True
    else:
        session["iframe_embeded"] = False


@bp.app_context_processor
def inject_template_globals():
    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    return dict(company=company, integration=integration, plans=plans, pages=pages)


@bp.route("/cdn/<path:filename>")
def custom_static(filename):
    return send_from_directory(current_app.config["UPLOADED_IMAGES_DEST"], filename)


def redirect_url():
    return request.args.get("next") or request.referrer or url_for("index")


def index():
    return render_template("index.html")


@bp.route("/500")
def show_500():
    """Force 500 error"""
    return abort(500)


@bp.route("/choose")
def choose():
    # Note: Categories link to plans (via category.plans)
    categories = Category.query.order_by(Category.position).all()
    return render_template("choose.html", categories=categories)


@bp.route("/set_options/<plan_uuid>", methods=["GET", "POST"])
def set_options(plan_uuid):
    plan = Plan.query.filter_by(uuid=plan_uuid).first()

    if request.method == "POST":
        # Store chosen options in session
        session["chosen_option_ids"] = []
        for choice_group_id in request.form.keys():
            for option_id in request.form.getlist(choice_group_id):
                session["chosen_option_ids"].append(option_id)

        return redirect(url_for("checkout.new_customer", plan=plan_uuid))

    return render_template("set_options.html", plan=plan)


@bp.route("/page/<path>", methods=["GET"])
def custom_page(path):
    page = Page.query.filter_by(path=path).first()
    # Check if private page & enforce
    blocked, redirect = check_private_page(page.id)
    if blocked:
        return redirect
    try:
        with open(
            Path(str(current_app.config["THEME_PATH"]), page.template_file)
        ) as fh:
            body = fh.read()
    except FileNotFoundError as e:
        print(e)
        return "Template not found for this page.", 404

    page_header = """
        {% extends "layout.html" %}
        {% block title %} {{ title }} {% endblock title %}

        {% block hero %}
            <div class="section-hero px-2 mb-4">
                <div class="wrapper mx-auto">
                    <div class="container py-5">
                        <h2 class="title-1">{{ title }}</h2>
                    </div>
                </div>
            </div>

        {% endblock %}
        {% block body %}
        <div class="section mx-auto">
          <div class="container mx-auto">

    """
    # Inject custom styles into the footer also
    custom_css = inject_custom_style()["custom_css"]
    page_footer = custom_css
    page_footer += """
          </div><!-- end container -->
        </div><!-- end section -->
        {% endblock body %}
    """
    try:
        rtemplate = Environment(
            loader=FileSystemLoader(str(current_app.config["THEME_PATH"]))
        ).from_string(page_header + body + page_footer)
    except jinja2.exceptions.TemplateAssertionError as e:
        return f"Page needs updating: {e}"

    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    template = rtemplate.render(
        company=company,
        integration=integration,
        plans=plans,
        pages=pages,
        session=session,
        g=g,
        url_for=url_for,
        title=page.page_name,
    )

    return template


@bp.route("/withgoogle")
def google_signin():

    state = str(os.urandom(12))
    session["state"] = state
    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    scope = current_app.config["GOOGLE_SCOPE"]

    redirect_url = f"https://accounts.google.com/o/oauth2/v2/auth?scope={scope}&\
access_type=offline&\
include_granted_scopes=true&\
response_type=code&\
state={state}&\
redirect_uri={redirect_uri}&\
client_id={client_id}"
    return redirect(redirect_url)


@bp.route("/google-oauth2callback/")
def google_return():
    client_id = current_app.config["GOOGLE_CLIENT_ID"]
    redirect_uri = current_app.config["GOOGLE_REDIRECT_URI"]
    client_secret = current_app.config["GOOGLE_CLIENT_SECRET"]

    # Verify state token
    if request.args["state"] != session["state"]:
        login_url = url_for("auth.login")
        msg = f"Google could not sign you in. Try loging in with email and password: <a href='{login_url}'>Login</a>. The error was Invalid state token"  # noqa: E501
        return msg, 403

    # From the returned url, exchange authorization code for an access token
    authorization_code = request.args.get("code", None)

    if authorization_code is None:
        return "Error: Google did not give authorization_code"

    # Get an access token by calling https://oauth2.googleapis.com/token,
    # passing the authorization_code.
    data = {
        "code": authorization_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    resp = requests.post("https://oauth2.googleapis.com/token", data=data)
    if resp.status_code != 200:
        login_url = url_for("auth.login")
        return f"Google signin didn't signin didn't work. Please login with your email/password instead: <a href='{login_url}'>Login</a>"  # noqa: E501

    # Try and get access token from the response
    access_token = resp.json().get("access_token", None)
    refresh_token = resp.json().get("refresh_token", None)
    scopes_permitted = resp.json().get("scope", None)
    token_type = resp.json().get("token_type", None)

    # Put access token and refresh_token in session (normally would store in database) # noqa
    session["access_token"] = access_token
    session["refresh_token"] = refresh_token
    session["scope"] = scopes_permitted
    session["token_type"] = token_type

    # Get user profile information (name, email)
    headers = {"Authorization": "Bearer " + access_token}
    resp = requests.get(
        "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
        headers=headers,  # noqa
    )
    data = resp.json()
    email = data["email"]
    session["email"] = data["email"]
    session["family_name"] = data["family_name"]
    session["given_name"] = data["given_name"]

    if current_app.config["THEME_NAME"] == "builder":
        return redirect(url_for("builder.start_building", email=email))
    else:
        if oauth_login_user(email):
            start_new_user_session(email)
            return redirect(url_for("admin.dashboard"))
        else:
            login_url = url_for("auth.login")
            return f"User not found, try username/password please login instead of Google signin. <a href='{login_url}'>Login</a>"  # noqa: E501
