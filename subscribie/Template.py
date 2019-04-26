from .jamla import Jamla
import jinja2
import os
import git
import subprocess


def load_theme(app):
    jamlaApp = Jamla()
    jamla = jamlaApp.load(src=app.config["JAMLA_PATH"])
    print("load_theme()")
    print("JAMLA_PATH is: {}".format(app.config["JAMLA_PATH"]))
    print("TEMPLATE_BASE_DIR is: {}".format(app.config["TEMPLATE_BASE_DIR"]))
    print("Theme name is: {}".format(jamla["theme"]["name"]))
    try:
        if os.path.exists(
            app.config["TEMPLATE_BASE_DIR"] + "/theme-" + jamla["theme"]["name"]
        ):
            themepath = "".join(
                [
                    app.config["TEMPLATE_BASE_DIR"],
                    "theme-",
                    jamla["theme"]["name"],
                    "/",
                    jamla["theme"]["name"],
                ]
            )
            static_folder = (
                app.config["TEMPLATE_BASE_DIR"]
                + "/theme-"
                + jamla["theme"]["name"]
                + "/static"
            )
        else:
            if "src" in jamla["theme"]:
                # Attempt to load theme from src
                try:
                    print("NOTICE: Importing theme")
                    dest = "".join(
                        [
                            app.config["TEMPLATE_BASE_DIR"],
                            "theme-",
                            jamla["theme"]["name"],
                            "/",
                        ]
                    )
                    git.Repo.clone_from(jamla["theme"]["src"], dest)
                except git.exc.GitCommandError:
                    raise
                themepath = "".join(
                    [
                        app.config["TEMPLATE_BASE_DIR"],
                        "theme-",
                        jamla["theme"]["name"],
                        "/",
                        jamla["theme"]["name"],
                    ]
                )
                static_folder = dest + "/static"
                # Update jamla path and template folder path
                subprocess.call(
                    "subscribie \
                     setconfig \
                     --TEMPLATE_FOLDER {}\
                     --STATIC_FOLDER {}".format(
                        themepath, static_folder
                    ),
                    shell=True,
                )
    except Exception as e:
        print("Falling back to default theme")
        print(e)
        themepath = app.config["TEMPLATE_BASE_DIR"] + "theme-jesmond/jesmond/"
    my_loader = jinja2.ChoiceLoader(
        [jinja2.FileSystemLoader(themepath), app.jinja_loader]
    )
    app.jinja_loader = my_loader
    try:
        app.static_folder = static_folder
    except NameError:
        print("Fallback to jesmon theme")
        app.static_folder = app.config["TEMPLATE_BASE_DIR"] + "theme-jesmond/static/"
