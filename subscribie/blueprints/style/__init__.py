from flask import Blueprint, request, render_template, abort, flash, redirect
from subscribie.auth import login_required
from subscribie.models import database, ModuleStyle
from jinja2 import TemplateNotFound
from flask import Markup

module_style_shop = Blueprint("style", __name__, template_folder="templates")


@module_style_shop.app_context_processor
def inject_custom_style():
    # Styles are injected into the base of the template
    # output as inline css using <style> tags.
    styles = ModuleStyle.query.first()
    if styles is not None:
        global_css = styles.css
        bg_primary = styles.bg_primary
    else:
        global_css = ""
        bg_primary = ""
    css_custom_properties = ""

    # Apply default primary colour
    if bg_primary == "":
        css_custom_properties += "".join(
            [
                """:root {
                --bg-primary: rgb(0, 123, 255);
            }"""
            ]
        )
    else:
        css_custom_properties += "".join(
            [
                """
      :root {
        --bg-primary: """,
                bg_primary,
                "}",
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
        css = ModuleStyle.query.first()
        if css is not None:
            customCSS = css.css
            bg_primary = css.bg_primary
        else:
            customCSS = ""
            bg_primary = ""
        return render_template(
            "show-custom-css.html", customCSS=customCSS, bg_primary=bg_primary
        )
    except TemplateNotFound:
        abort(404)


@module_style_shop.route("/style-shop", methods=["POST"])
@login_required
def save_custom_style():
    """Remove all old css, and replace with submitted css"""
    css = request.form.get("css", "")
    bg_primary = request.form.get("bg_primary", "")
    print(css)
    # Delete previous css entry
    ModuleStyle.query.delete()
    # Add new style css entry
    style = ModuleStyle()
    style.css = css
    style.bg_primary = bg_primary
    database.session.add(style)
    database.session.commit()

    flash(Markup('Styling updated. View your <a href="/">updated shop</a>'))
    return redirect("/")
