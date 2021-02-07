from subscribie.auth import check_private_page
from pathlib import Path
import jinja2
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
from .models import (
    Company,
    Plan,
    Integration,
    Page,
)
from flask_migrate import upgrade
from subscribie.blueprints.style import inject_custom_style

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
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    return render_template("choose.html", plans=plans)


@bp.route("/set_options/<plan_uuid>", methods=["GET", "POST"])
def set_options(plan_uuid):
    plan = Plan.query.filter_by(uuid=plan_uuid).first()

    if request.method == "POST":
        # Store chosen options in session
        session["chosen_option_ids"] = []
        for choice_group_id in request.form.keys():
            for option_id in request.form.getlist(choice_group_id):
                session["chosen_option_ids"].append(option_id)

        return redirect(url_for("views.new_customer", plan=plan_uuid))

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

            <div class="container">
              <div class="row">
                <div class="col-md-8 pl-0">
                  <h1 class="h1 text-white font-weight-bold">{{ title }}</h1>
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
