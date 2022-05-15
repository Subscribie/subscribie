import logging
from subscribie.auth import check_private_page
from pathlib import Path
import jinja2
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
    Markup,
)
from .models import Company, Plan, Integration, Page, Category, Setting
from flask_migrate import upgrade
from subscribie.blueprints.style import inject_custom_style
from subscribie.database import database
from subscribie.signals import journey_complete, signal_payment_failed
from subscribie.receivers import (
    receiver_send_shop_owner_new_subscriber_notification_email,
    receiver_send_subscriber_payment_failed_notification_email,
)
from subscribie.blueprints.admin.stats import (
    get_number_of_active_subscribers,
    get_monthly_revenue,
)
import pycountry

log = logging.getLogger(__name__)

bp = Blueprint("views", __name__, url_prefix=None)


# Connect signals to recievers
journey_complete.connect(receiver_send_shop_owner_new_subscriber_notification_email)
signal_payment_failed.connect(
    receiver_send_subscriber_payment_failed_notification_email
)


@bp.before_app_first_request
def migrate_database():
    """Migrate database when app first boots"""
    log.info("Migrating database")
    upgrade(
        directory=Path(current_app.config["SUBSCRIBIE_REPO_DIRECTORY"] + "/migrations")
    )


@bp.before_app_request
def on_each_request():
    # Detect country code if present in the request from proxy
    # the requesting country must be detected by the upstream
    # proxy, and that proxy must inject the header 'Geo-Country-Code'
    # into the request in order for Subscribie to read it.
    # https://github.com/Subscribie/subscribie/issues/886
    # See also https://github.com/KarmaComputing/geo-location-ip-country-serverside
    geo_country_code_header = request.headers.get("Geo-Country-Code")
    try:
        countryObj = pycountry.countries.get(alpha_2=geo_country_code_header)
    except LookupError as e:  # noqa: F841
        log.debug("Unable to get geo country from request header: {e}")

    # Dynamic country detection
    if countryObj is not None:
        country = {
            "alpha_2": countryObj.alpha_2,
            "alpha_3": countryObj.alpha_3,
            "flag": countryObj.flag,
            "name": countryObj.name,
            "numeric": countryObj.numeric,
            "official_name": countryObj.official_name,
        }
        session["country"] = country
        session["country_code"] = countryObj.alpha_2
    else:
        # Default to default country selection
        # TODO As a shop owner I can set the default country of my shop
        countryObj = pycountry.countries.get(alpha_2="GB")
        country = {
            "alpha_2": countryObj.alpha_2,
            "alpha_3": countryObj.alpha_3,
            "flag": countryObj.flag,
            "name": countryObj.name,
            "numeric": countryObj.numeric,
            "official_name": countryObj.official_name,
        }
        session["country"] = country
        session["country_code"] = countryObj.alpha_2

    # Add all plans to one
    if Category.query.count() == 0:  # If no categories, create default
        category = Category()
        category.name = "Make your choice"
        # Add all plans to this category
        plans = Plan.query.all()
        for plan in plans:
            plan.category = category
        database.session.add(category)


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
        log.info("Loading from within iframe")
        session["iframe_embeded"] = True
    else:
        session["iframe_embeded"] = False


@bp.app_context_processor
def inject_template_globals():
    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    setting = Setting.query.first()
    if setting is None:
        setting = Setting()
        database.session.add(setting)
        database.session.commit()
    custom_code = Setting.query.first().custom_code
    return dict(
        company=company,
        integration=integration,
        plans=plans,
        pages=pages,
        custom_code=Markup(custom_code),
    )


@bp.route("/health")
def health():
    return "OK", 200


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


@bp.route("/open")
def stats():
    """Open stats"""
    return {
        "active_subscribers": get_number_of_active_subscribers(),
        "monthly_revenue": get_monthly_revenue(),
    }


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
    if page is None:
        return "Page not found", 404
    # Check if private page & enforce
    blocked, redirect = check_private_page(page.id)
    if blocked:
        return redirect
    try:
        with open(
            Path(str(current_app.config["CUSTOM_PAGES_PATH"]), page.template_file)
        ) as fh:
            body = fh.read()
    except FileNotFoundError as e:
        log.error(f"Template not found FileNotFoundError. {e}")
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
        rtemplate = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(current_app.config["THEME_PATH"]))
        ).from_string(page_header + body + page_footer)
    except jinja2.exceptions.TemplateAssertionError as e:
        log.error(f"Error updating custom page: {e}")
        return "Unable to update page. We have been notified. Sorry about that!", 500

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


@bp.route("/plan/<uuid>", defaults={"plan_title": None})
@bp.route("/plan/<uuid>/<plan_title>")
def view_plan(uuid, plan_title=None):
    """
    Note: "plan_name" is not used, and is also
          optional. It's just there to make
          urls look 'pretty'
          when humans share them.
    """
    # fetch plan from db
    plan = Plan.query.filter_by(uuid=uuid).first()
    if plan is None:
        return "Plan not found. Visit <a href='/'>home</a>"
    elif plan.archived:
        return "This plan has been archived. Visit <a href='/'>home</a>"

    return render_template("view-plan.html", plan=plan)
