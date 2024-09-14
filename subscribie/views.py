from .logger import logger  # noqa: F401
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
)
from markupsafe import Markup
from .models import (
    Company,
    Plan,
    Integration,
    Page,
    Category,
    Setting,
    PaymentProvider,
    Question,
    QuestionOption,
)
from subscribie.blueprints.style import inject_custom_style
from subscribie.database import database
from subscribie.signals import register_signal_handlers, signal_new_subscriber

from subscribie.blueprints.admin.stats import (
    get_number_of_active_subscribers,
    get_monthly_revenue,
)
from subscribie.utils import (
    get_geo_currency_symbol,
    get_geo_currency_code,
    get_shop_default_country_code,
    get_shop_default_currency_symbol,
    currencyFormat,
)
import pycountry
from types import SimpleNamespace
from flask_babel import Domain
from urllib.parse import urlparse
from pathlib import PurePosixPath
from urllib.parse import unquote
from sqlalchemy import func
from subscribie.notifications import newSubscriberEmailNotification

log = logging.getLogger(__name__)

bp = Blueprint("views", __name__, url_prefix=None)


# Connect signals to recievers
register_signal_handlers()


@bp.before_app_request
def on_each_request():
    # Detect country code if present in the request from proxy
    # the requesting country must be detected by the upstream
    # proxy, and that proxy must inject the header 'Geo-Country-Code'
    # into the request in order for Subscribie to read it.
    # https://github.com/Subscribie/subscribie/issues/886
    # See also https://github.com/KarmaComputing/geo-location-ip-country-serverside

    # Assume country detection will fail by default
    session["fallback_default_country_active"] = False
    countryObj = None

    # Try to get Geo-Country-Code
    geo_country_code_header = request.headers.get("Geo-Country-Code")
    try:
        countryObj = pycountry.countries.get(alpha_2=geo_country_code_header)
    except LookupError as e:  # noqa: F841
        log.debug(f"Unable to get geo country from request header: {e}")

    # Dynamic country detection
    if countryObj is not None:
        country = {
            "alpha_2": countryObj.alpha_2,
            "alpha_3": countryObj.alpha_3,
            "flag": countryObj.flag,
            "name": countryObj.name,
            "numeric": countryObj.numeric,
        }
        session["country"] = country
        session["country_code"] = countryObj.alpha_2
    else:
        # Default to default country selection
        # TODO As a shop owner I can set the default country of my shop
        fallback_default_country = get_shop_default_country_code()
        log.debug(
            f"Unable to get geo country from request headers. Falling back to: {fallback_default_country}"  # noqa: E501
        )
        countryObj = pycountry.countries.get(alpha_2=fallback_default_country)
        assert countryObj is not None
        country = {
            "alpha_2": countryObj.alpha_2,
            "alpha_3": countryObj.alpha_3,
            "flag": countryObj.flag,
            "name": countryObj.name,
            "numeric": countryObj.numeric,
        }
        session["country"] = country
        session["country_code"] = countryObj.alpha_2
        session["fallback_default_country_active"] = True
        log.debug(f'session country is set to: {session["country"]}')
        log.debug(f'session country_code is set to: {session["country_code"]}')
        log.debug(
            f'session fallback_default_country_active is: {session["fallback_default_country_active"]}'  # noqa: E501
        )

    # Add all plans to one
    if Category.query.count() == 0:  # If no categories, create default
        category = Category()
        # Note this string is not translated since is populated
        # during bootstrap. category.name titles may be edited in the
        # admin dashboard in the 'Manage Categories' section
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
    from subscribie.settings import settings as internal_settings
    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    settings = Setting.query.first()
    custom_code = settings.custom_code
    SENTRY_SDK_SESSION_REPLAY_ID = internal_settings.get("SENTRY_SDK_SESSION_REPLAY_ID")
    geo_currency_symbol = get_geo_currency_symbol()
    default_currency_symbol = get_shop_default_currency_symbol()
    currency_format = currencyFormat

    return dict(
        company=company,
        integration=integration,
        plans=plans,
        pages=pages,
        custom_code=Markup(custom_code),
        SENTRY_SDK_SESSION_REPLAY_ID=SENTRY_SDK_SESSION_REPLAY_ID,
        geo_currency_symbol=geo_currency_symbol,
        get_geo_currency_code=get_geo_currency_code,
        default_currency_symbol=default_currency_symbol,
        currency_format=currency_format,
        settings=settings,
    )


@bp.route("/health")
def health():
    return "OK", 200


@bp.route("/test-signal_new_subscriber")
def test_signal_new_subscriber():
    signal_new_subscriber.send(subscription_uuid="test")
    return "Test signal_new_subscriber email generated."


@bp.route("/notification")
def test_notifications():
    log.debug("Test debug notification")
    log.info("Test info notification")
    log.warning("Test warning notification")
    log.error("Test error notification")
    log.critical("Test critical notification")
    return """Test notification sent.\n
    If handlers are configured correctly, then notification(s) will appear in the respective handler(s).\n
    See also https://docs.subscribie.co.uk/docs/architecture/logging/"""  # noqa: E501


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
    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_active is None:
        payment_provider.stripe_active = False

    """Open stats"""
    return {
        "active_subscribers": get_number_of_active_subscribers(),
        "monthly_revenue": get_monthly_revenue(),
        "stripe_active": payment_provider.stripe_active,
        "stripe_livemode": payment_provider.stripe_livemode,
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
        session["chosen_question_ids_answers"] = []
        for form_control_id in request.form.keys():
            chosen_option_id = int(request.form.getlist(form_control_id)[0])
            session["chosen_option_ids"].append(chosen_option_id)
        # If plan has Questions, ask them:
        if plan.questions:
            return redirect(url_for("views.set_questions", plan_uuid=plan_uuid))
        return redirect(url_for("checkout.new_customer", plan=plan_uuid))

    return render_template("set_options.html", plan=plan)


@bp.route("/set_questions/<plan_uuid>", methods=["GET", "POST"])
def set_questions(plan_uuid):
    plan = Plan.query.filter_by(uuid=plan_uuid).first()

    if request.method == "POST":
        # Store question answers in session
        session["chosen_question_ids_answers"] = []
        for form_control_id in request.form.keys():
            # Question form are named 'question-<index>'
            # Choice group options are named: '<index>'
            question_id = int(form_control_id.replace("question-", ""))
            question = Question.query.get(question_id)
            # If question has options, store the value chosen,
            # otherwise, take the form contol <input /> value
            if question.options:
                question_answer = QuestionOption.query.get(
                    request.form.get(form_control_id)
                ).title
            else:
                question_answer = request.form.get(form_control_id)
            answer = {"question_id": question_id, "answer": question_answer}
            session["chosen_question_ids_answers"].append(answer)
        session["questions_form_completed"] = True
        return redirect(url_for("checkout.new_customer", plan=plan_uuid))
    # Sort the questions
    plan.questions.sort(key=lambda question: question.order or 0, reverse=False)
    return render_template("set_questions.html", plan=plan)


@bp.route("/page/<path>", methods=["GET"])
def custom_page(path):
    page = Page.query.filter_by(path=path).first()
    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    settings = Setting.query.first()
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

        def _get_current_context():
            if not g:
                return None

            if not hasattr(g, "_flask_babel"):
                g._flask_babel = SimpleNamespace()

            return g._flask_babel

        def get_domain():
            ctx = _get_current_context()
            if ctx is None:
                # this will use NullTranslations
                return Domain()

            try:
                return ctx.babel_domain
            except AttributeError:
                pass

            babel = current_app.extensions["babel"]
            return babel.instance.domain_instance

        def get_translations():
            """Returns the correct gettext translations that should be used for
            this request.  This will never fail and return a dummy translation
            object if used outside of the request or if a translation cannot be
            found.
            """
            return get_domain().get_translations()

        rtemplate = jinja2.Environment(
            extensions=["jinja2.ext.i18n"],
            loader=jinja2.FileSystemLoader(str(current_app.config["THEME_PATH"])),
        )
        rtemplate.install_gettext_callables(
            lambda x: get_translations().ugettext(x),
            lambda s, p, n: get_translations().ungettext(s, p, n),
            newstyle=True,
        )
        rtemplate = rtemplate.from_string(page_header + body + page_footer)
    except jinja2.exceptions.TemplateAssertionError as e:
        log.error(f"Error updating custom page: {e}")
        return "Unable to update page. We have been notified. Sorry about that!", 500

    template = rtemplate.render(
        company=company,
        integration=integration,
        plans=plans,
        pages=pages,
        session=session,
        g=g,
        url_for=url_for,
        title=page.page_name,
        settings=settings,
    )

    return template


@bp.route("/plan/<uuid>", defaults={"plan_title": None})
@bp.route("/plan/<uuid>/<plan_title>")
def view_plan(uuid, plan_title=None):
    """
    Match on plan uuid, or fallback to plan name.

    Note: "uuid" may refer to an archived plan for backward
         compatibility with published links.
         See https://github.com/Subscribie/subscribie/issues/1364
    """
    # fetch plan from db
    plan = Plan.query.filter_by(uuid=uuid).first()
    if plan is None:
        # Try to locate plan by title only
        url = urlparse(request.url)
        request_path = PurePosixPath(url.path).parts
        requested_plan_name_slug = unquote(request_path[3])
        plan = Plan.query.filter(
            func.lower(Plan.title) == requested_plan_name_slug.lower()
        ).first()

    if plan is None:
        return "Plan not found. Visit <a href='/'>home</a>"
    elif plan.archived:
        return "This plan has been archived. Visit <a href='/'>home</a>"

    return render_template("view-plan.html", plan=plan)


@bp.route("/set-language", methods=["GET", "POST"])
def set_language_code():
    log.debug("In set_language_code")
    # Set language code in session
    language_code = request.form.get("language_code", None)
    log.debug(f"selected language code was {language_code}")
    session["language_code"] = language_code
    return redirect("/")
