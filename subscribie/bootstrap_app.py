from pathlib import Path
from flask_migrate import upgrade
from .logger import logger  # noqa: F401
import logging
from flask import current_app
from subscribie.database import database
from subscribie.models import Setting

log = logging.getLogger(__name__)


def migrate_database():
    """Migrate database when app first boots"""
    log.info("Migrating database")
    upgrade(
        directory=Path(current_app.config["SUBSCRIBIE_REPO_DIRECTORY"] + "/migrations")
    )


def set_app_default_settings():
    """Pre-populate the Settings model with the column insertion defaults.

    If the Settings model is empty, pre-populate the database with the column
    insertion defaults (see model.py -> class Settings).

    Note this does not relate to .env settings. See README.md
    The Settings stored in the Settings database model are for
    user controllable settings which may be changed at runtime
    without an application restart.

    Issue #1262
    https://github.com/Subscribie/subscribie/issues/1262
    """
    setting = Setting.query.first()
    if setting is None:
        setting = Setting()
        database.session.add(setting)
        database.session.commit()
