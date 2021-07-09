import logging
from flask import Blueprint, url_for, jsonify
from subscribie.models import Page

log = logging.getLogger(__name__)

apiv1 = Blueprint("apiv1", __name__, template_folder="templates")


@apiv1.route("/pages", methods=["GET"])
def apiv1_list_pages():
    pages = Page.query.all()
    urls = []
    for page in pages:
        urls.append(
            {
                "url": url_for(
                    "views.custom_page", path=page.path, _external=True, _scheme="https"
                )
            }
        )
    return jsonify(urls)
