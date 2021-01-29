from flask import Blueprint, request, render_template, abort, redirect
from subscribie.auth import login_required
from subscribie.models import database, ModuleStyle
from jinja2 import TemplateNotFound
import json

module_style_shop = Blueprint("style", __name__, template_folder="templates")


@module_style_shop.app_context_processor
def inject_custom_style():
    # Styles are injected into the base of the template
    # output as inline css using <style> tags.
    global_css = ""
    # Set default colours
    css_properties_json = {"primary": "#2575fc", "secondary": "", "info": ""}
    css_custom_properties = ""

    styles = ModuleStyle.query.first()
    if styles is not None:
        global_css = styles.css
        try:
            css_properties_json = json.loads(styles.css_properties_json)
            css_custom_properties += "".join(
                [
                    ":root {",
                    "--bg-primary:",
                    css_properties_json["primary"],
                    ";" "--bg-secondary:",
                    css_properties_json["secondary"],
                    ";",
                    "--bg-info:",
                    css_properties_json["info"],
                    ";" "}",
                ]
            )
        except Exception:
            pass
    else:  # Fallback to default
        css_custom_properties += "".join(
            [
                ":root {",
                "--bg-primary:",
                css_properties_json["primary"],
                ";" "--bg-secondary:",
                css_properties_json["secondary"],
                ";",
                "--bg-info:",
                css_properties_json["info"],
                ";" "}",
            ]
        )

    # Override bootstrap
    css_custom_properties += "".join(
        [
            """.bg-info {
      background-color: var(--bg-primary) !important;
    }""",
            """
    .btn-primary {
      background-color: var(--bg-primary) !important;
      border-color: var(--bg-primary) !important;
    }
    """,
            """
    .navbar-dark .navbar-nav :hover {
      background-color: var(--bg-primary) !important;
    }
    """,
            """
    .bg-primary {
      background-color: var(--bg-primary) !important;
    }""",
            """
    .btn-success {
      background-color: var(--bg-primary) !important;
      border-color: var(--bg-primary) !important;
    }""",
        ]
    )

    # Wrap style tags
    custom_css = "".join(
        ['<style type="text/css">', css_custom_properties, global_css, "</style>"]
    )

    return dict(custom_css=custom_css)


def getCustomCSS():
    """Return custom css"""
    css = ModuleStyle.query.first()
    if css:
        return css.css
    else:
        return None


@module_style_shop.route("/style_shop/index")  # Define a module index page
@module_style_shop.route("/style-shop")
@login_required
def style_shop():
    try:
        # Load custom css rules (if any) and display in an editable textbox
        css_style = ModuleStyle.query.first()
        if css_style is not None and css_style.css != "":
            customCSS = css_style.css
            css_properties = json.loads(css_style.css_properties_json)
        else:
            customCSS = ""
            css_properties = ""

        return render_template(
            "show-custom-css.html", customCSS=customCSS, css_properties=css_properties
        )
    except TemplateNotFound:
        abort(404)


@module_style_shop.route("/style-shop", methods=["POST"])
@login_required
def save_custom_style():
    """Remove all old css, and replace with submitted css"""

    # Convert POST data to json and save to the database column
    css_properties = json.dumps(request.form.to_dict())
    global_css = request.form.get("css", "")
    print(global_css)
    # Delete previous css entry
    ModuleStyle.query.delete()
    # Add new style css entry
    style = ModuleStyle()
    style.css_properties_json = css_properties
    style.css = global_css
    database.session.add(style)
    database.session.commit()

    return redirect("/")
