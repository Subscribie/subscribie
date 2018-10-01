from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

admin_theme = Blueprint('admin', __name__, template_folder='templates',
                        static_folder='static')

@admin_theme.route('/testing')
def show():
    return render_template('admin/index.html')
