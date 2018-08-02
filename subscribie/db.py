from flask import current_app, g
from subscribie import Jamla


def get_db():
    if 'db' not in g:
	jamlaApp = Jamla()                                                           
	g.jamla = jamlaApp.load(src=current_app.config['JAMLA_PATH'])
    return g.jamla

def close_db(e=None):
    db = g.pop('jamla', None)


def init_app(app):
    app.teardown_appcontext(close_db)
