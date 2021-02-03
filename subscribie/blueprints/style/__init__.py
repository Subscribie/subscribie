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
    js_inject = ""
    # Set default colours
    styles = ModuleStyle.query.first()
    if styles is not None:
        global_css = styles.css

    # Js primary colours injection via javascript
    try:
        css_properties_json = json.loads(styles.css_properties_json)
        primary = css_properties_json["primary"]
        hsl_h = primary.split(",")[0]
        hsl_s = primary.split(",")[1]
        hsl_l = primary.split(",")[2]
        js_inject = """<script>
        document.documentElement.style.setProperty('--primary-color-hs', [Math.round({hsl_h}), Math.round({hsl_s} * 100) + '%'].join());
        document.documentElement.style.setProperty('--primary-color-l', Math.round({hsl_l} * 100) + '%');
        </script>
        """.format(
            hsl_h=hsl_h, hsl_s=hsl_s, hsl_l=hsl_l
        )
    except Exception as e:
        print(e)
        print("Could not load custom css properties")
    # Raw global css overrises
    custom_css = "".join([js_inject, '<style type="text/css">', global_css, "</style>"])

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
        css_primary = ""
        customCSS = ""
        if css_style is not None and css_style.css != "":
            customCSS = css_style.css
        if css_style is not None and css_style.css_properties_json != "":
            try:
                css_properties = json.loads(css_style.css_properties_json)
                parts = css_properties["primary"].split(",")
                css_primary = f"hsl({parts[0]}, {parts[1]}, {parts[2]})"
            except Exception as e:
                print(e)
                print("Could not load css_style.css_properties_json")
        else:
            customCSS = ""
            css_properties = ""

        return render_template(
            "show-custom-css.html", customCSS=customCSS, css_primary=css_primary
        )
    except TemplateNotFound:
        abort(404)


@module_style_shop.route("/style-shop", methods=["POST"])
@login_required
def save_custom_style():
    """Remove all old css, and replace with submitted css"""
    styles = ModuleStyle.query.first()
    if styles is None:
        styles = ModuleStyle()

    if request.form.get("global_css", None):
        # Save global css
        global_css = request.form.get("global_css", "")
        styles.css = global_css
    else:
        styles.css = ""  # Remove global css styles as empty
        # Save custom hsl colours
        css_properties = json.dumps(request.form.to_dict())
        if "primary" in css_properties:
            styles.css_properties_json = css_properties

    database.session.add(styles)
    database.session.commit()

    return redirect("/")
