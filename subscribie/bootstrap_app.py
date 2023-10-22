from pathlib import Path
from flask_migrate import upgrade
from .logger import logger  # noqa: F401
import logging
from flask import current_app
from subscribie.database import database
from subscribie.models import Setting, Plan, Category

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


def set_plans_default_category():
    """Add all plans to a default category if they are not associated with one"""
    # Add all plans to one
    if Category.query.count() == 0:  # If no categories, create default
        category = Category()
        # Note this string is not translated since is populated
        # during bootstrap. category.name titles may be edited in the
        # admin dashboard in the 'Manage Categories' section
        category.name = "Make your choice"
        # Add all plans to this category
        plans = Plan.query.all()
        for plan in plans:
            plan.category = category
        database.session.add(category)
        database.session.commit()
