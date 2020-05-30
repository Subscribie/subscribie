import sqlite3

from flask import current_app, g

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DB_FULL_PATH"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db
