from flask import (Blueprint, request, render_template, abort, flash, url_for, 
    redirect)
from subscribie.auth import login_required
from subscribie import current_app
from subscribie.models import database, ModuleStyle
from jinja2 import TemplateNotFound
from flask import Markup

module_style_shop = Blueprint('style', __name__, template_folder='templates')

@module_style_shop.app_context_processor
def inject_custom_style():
    # Styles are injected into the base of the template
    # output as inline css using <style> tags.
    css = getCustomCSS()
    # Wrap style tags
    if css is not None:
        custom_css = ''.join(['<style type="text/css">', css, '</style>'])
        return dict(custom_css=custom_css)
    else:
        return dict()

def getCustomCSS():
    """Return custom css"""
    css = ModuleStyle.query.first()
    if css:
        return css.css
    else:
        return None

@module_style_shop.route('/style_shop/index') # Define a module index page
@module_style_shop.route('/style-shop')
@login_required
def style_shop():
    try:
        # Load custom css rules (if any) and display in an editable textbox
        customCSS = getCustomCSS()
        if customCSS is None:
            customCSS = ''
        return render_template('show-custom-css.html', customCSS=customCSS)
    except TemplateNotFound:
        abort(404)

@module_style_shop.route('/style-shop', methods=['POST'])
@login_required
def save_custom_style():
    """Remove all old css, and replace with submitted css"""
    css = request.form['css']
    print(css)
    # Delete previous css entry
    ModuleStyle.query.delete()
    # Add new style css entry
    style = ModuleStyle()
    style.css = css
    database.session.add(style)
    database.session.commit()

    flash(Markup('Styling updated. View your <a href="/">updated shop</a>'))
    return redirect(url_for('style_shop.style_shop'))
