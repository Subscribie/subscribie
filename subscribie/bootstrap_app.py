from pathlib import Path
from flask_migrate import upgrade
from .logger import logger  # noqa: F401
import logging
from flask import current_app

log = logging.getLogger(__name__)


def migrate_database():
    """Migrate database when app first boots"""
    log.info("Migrating database")
    upgrade(
        directory=Path(current_app.config["SUBSCRIBIE_REPO_DIRECTORY"] + "/migrations")
    )
