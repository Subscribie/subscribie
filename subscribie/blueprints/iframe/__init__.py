from flask import (Blueprint, render_template, abort, request, redirect)
from jinja2 import TemplateNotFound
from subscribie.auth import login_required

module_iframe_embed = Blueprint('iframe', __name__, template_folder='templates')

@module_iframe_embed.route('/show-iframe-embed')
@login_required
def get_iframe_embed():
  """Set optimised title tags for your pages."""
  iframe = '''<iframe src={} width="100%" height="800px" scrolling="auto"
                allowfullscreen="true"
                title="Subscription shop">
        </iframe>
        '''.format(request.host_url)
  try:
    return render_template('show-iframe-embed.html', iframe=iframe)
  except TemplateNotFound:
    abort(404)