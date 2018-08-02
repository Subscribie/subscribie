from subscribie import Jamla
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_jamla():
    if 'jamla' not in g:
	jamlaApp = Jamla()                                                           
	g.jamla = jamlaApp.load(src=current_app.config['JAMLA_PATH'])
    return g.jamla


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config["DB_FULL_PATH"],
                               detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('jamla', None)

def init_db():
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initalized the database.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
