import jinja2
from pathlib import Path


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

    staticFolder = Path(
        app.config["TEMPLATE_BASE_DIR"],
        "theme-" + app.config["THEME_NAME"],
        "static",
    ).resolve()

    # Set THEME_PATH
    app.config["THEME_PATH"] = themePath

    my_loader = jinja2.ChoiceLoader(
        [jinja2.FileSystemLoader(str(themePath)), app.jinja_loader]
    )
    app.jinja_loader = my_loader
    app.static_folder = str(staticFolder)
