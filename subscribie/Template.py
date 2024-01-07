import jinja2
from pathlib import Path
import logging
from flask import abort

log = logging.getLogger(__name__)


def load_theme(app):
    """
    Set theme path and static assets path.

    Reminder on theme paths:

    Themes start from TEMPLATE_BASE_DIR e.g /tmp/themes
    You might have two themes:
      - /tmp/themes/themeOne
      - /tmp/themes/themeTwo

    All themes have a `static` folder for their assets,
    and a folder named the same as the theme name for the
    template files. e.g. For themeOne

      - /tmp/themes/themeOne/static (for static assets such as images, css)
      - /tmp/themes/themeOne/themeOne (for template files, such as layout.html)

    For themeTwo:

      - /tmp/themes/themeTwo/static (for static assets such as images, css)
      - /tmp/themes/themeOne/themeTwo (for template files, such as layout.html)
    """
    themePath = Path(
        app.config["TEMPLATE_BASE_DIR"],
        "theme-" + app.config["THEME_NAME"],
        app.config["THEME_NAME"],
    ).resolve()

    if themePath.exists() is False:
        log.warning(f"Configured themePath ({themePath}) does not exist.")

        log.warning("Attempting theme path from built-in package (if exists)")

        themePath = (
            Path(__file__)
            .parent.joinpath(
                f'themes/theme-{app.config["THEME_NAME"]}/{app.config["THEME_NAME"]}'
            )
            .resolve()
        )
        if themePath.exists() is False:
            abort(
                f"Unable to determine valid themePath. Check TEMPLATE_BASE_DIR in settings and THEME_NAME. TEMPLATE_BASE_DIR is set to {TEMPLATE_BASE_DIR} and THEME_NAME: {THEME_NAME}"  # noqa :E501
            )
        log.info(f"Default package themePath is set to {themePath} and exists.")
    else:
        log.info(f"Custom themePath is set to {themePath} and exists.")

    staticFolder = Path(
        app.config["TEMPLATE_BASE_DIR"],
        "theme-" + app.config["THEME_NAME"],
        "static",
    ).resolve()

    if staticFolder.exists() is False:
        log.warning(f"Configured staticFolder ({staticFolder}) does not exist.")

        log.warning(
            "Attempting to resolve staticFolder from built-in package (if exists)"
        )

        staticFolder = (
            Path(__file__)
            .parent.joinpath(Path(f'themes/theme-{app.config["THEME_NAME"]}', "static"))
            .resolve()
        )
        if staticFolder.exists() is False:
            abort(
                f"Unable to determine valid staticFolder. Check TEMPLATE_BASE_DIR in settings and THEME_NAME. TEMPLATE_BASE_DIR is set to {TEMPLATE_BASE_DIR} and THEME_NAME: {THEME_NAME}"  # noqa :E501
            )
        log.info(f"Default package staticFolder is set to {staticFolder} and exists.")
    else:
        log.info(f"Custom staticFolder is set to {staticFolder} and exists.")

    # Set THEME_PATH
    app.config["THEME_PATH"] = themePath

    my_loader = jinja2.ChoiceLoader(
        [
            # First attempt to get theme file from active theme
            jinja2.FileSystemLoader(str(themePath)),
            # Check if template is found in CUSTOM_PAGES_PATH
            jinja2.FileSystemLoader(str(app.config.get("CUSTOM_PAGES_PATH", None))),
            # Finally fallback to flask default template directory
            app.jinja_loader,
        ]
    )
    app.jinja_loader = my_loader
    app.static_folder = str(staticFolder)
