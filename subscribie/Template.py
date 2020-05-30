import jinja2
import os
import git
import subprocess
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
    p = Path()
    print("load_theme()")
    print("TEMPLATE_BASE_DIR is: {}".format(app.config["TEMPLATE_BASE_DIR"]))
    try:
        if p.joinpath(
            app.config["TEMPLATE_BASE_DIR"], "theme-" + app.config["THEME_NAME"]
        ).exists():
            themepath = p.joinpath(
                app.config["TEMPLATE_BASE_DIR"],
                "theme-" + app.config["THEME_NAME"],
                app.config["THEME_NAME"],
            )
            static_folder = themepath.joinpath("../", "static").resolve()
        else:
            if app.config["THEME_SRC"]:
                # Attempt to load theme from src
                try:
                    print("NOTICE: Importing theme")
                    dest = p.joinpath(
                        app.config["TEMPLATE_BASE_DIR"],
                        "theme-" + app.config["THEME_NAME"],
                    )
                    git.Repo.clone_from(app.config["THEME_SRC"], dest)
                except git.exc.GitCommandError:
                    raise
                themepath = p.joinpath(
                    app.config["TEMPLATE_BASE_DIR"],
                    "theme-" + app.config["THEME_NAME"],
                    app.config["THEME_NAME"],
                )
                static_folder = themepath.joinpath("../", "static").resolve()
                # Update jamla path and template folder path
                subprocess.call(
                    "subscribie \
                     setconfig \
                     --TEMPLATE_FOLDER {}\
                     --STATIC_FOLDER {}".format(
                        str(themepath), str(static_folder)
                    ),
                    shell=True,
                )
    except Exception as e:
        print("Falling back to default theme")
        print(e)
        p = Path()
        themepath = p.joinpath(
            app.config["TEMPLATE_BASE_DIR"], "theme-jesmond", "jesmond"
        )
    app.config["THEME_PATH"] = themepath
    my_loader = jinja2.ChoiceLoader(
        [jinja2.FileSystemLoader(str(themepath)), app.jinja_loader]
    )
    app.jinja_loader = my_loader
    try:
        app.static_folder = str(static_folder)
    except NameError:
        print("Fallback to jesmon theme")
        app.static_folder = p.joinpath(
            app.config["TEMPLATE_BASE_DIR"], "theme-jesmond/static/"
        )
