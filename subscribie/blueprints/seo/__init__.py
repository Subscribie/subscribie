import logging
from flask import Blueprint, render_template, abort, url_for, request, flash, redirect
from jinja2 import TemplateNotFound
from subscribie import current_app
from subscribie.auth import login_required
from base64 import urlsafe_b64encode, urlsafe_b64decode
import sqlite3

log = logging.getLogger(__name__)

module_seo_page_title = Blueprint("seo", __name__, template_folder="templates")


@module_seo_page_title.app_context_processor
def inject_page_title():
    title = getPathTitle(request.path)
    return dict(title=title)


@module_seo_page_title.route("/list-page-titles")
@login_required
def list_pages():
    rules = []
    for rule in current_app.url_map.iter_rules():
        # Ignore admin paths
        if (
            "/admin/" not in rule.rule
            and "/auth/" not in rule.rule
            and "/_uploads/" not in rule.rule
            and "/static/" not in rule.rule
            and "/up_front/" not in rule.rule
        ):
            rules.append(
                {
                    "path": rule,
                    "encodedPath": urlsafe_b64encode(str(rule).encode("ascii")),
                    "title": getPathTitle(str(rule)),
                }
            )

    try:
        return render_template("list-urls.html", rules=rules)
    except TemplateNotFound:
        abort(404)


def getPathTitle(path):
    """Return page title of a given path, or None"""
    con = sqlite3.connect(current_app.config["DB_FULL_PATH"])
    cur = con.cursor()
    res = cur.execute(
        "SELECT title FROM module_seo_page_title WHERE path = ?", (path,)
    ).fetchone()
    if res is None:
        return ""
    else:
        title = res[0]
        return title


@module_seo_page_title.route("/set-page-title/<encodedPath>", methods=["GET", "POST"])
@login_required
def set_page_title(encodedPath):
    path = urlsafe_b64decode(encodedPath).decode("utf-8")
    current_path_title = getPathTitle(path)
    if request.method == "GET":
        return render_template(
            "set-page-title.html", path=str(path), current_path_title=current_path_title
        )
    elif request.method == "POST":
        title = request.form["title"]
        con = sqlite3.connect(current_app.config["DB_FULL_PATH"])
        cur = con.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO module_seo_page_title (path, title) values (?,?)",
            (path, title),
        )
        con.commit()
        con.close()
        flash("Page title saved")
        return redirect(url_for("seo.list_pages"))
