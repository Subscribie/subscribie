import logging
from flask import Blueprint, url_for, jsonify
from subscribie.models import Page, Setting
from subscribie.database import database
from subscribie.auth import saas_api_only

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


@apiv1.route("/activate-shop", methods=["GET"])
@saas_api_only
def apiv1_activate_shop():
    setting = Setting.query.first()
    setting.shop_activated = 1
    database.session.commit()
    return jsonify({"msg": "shop activated"})


@apiv1.route("/deactivate-shop", methods=["GET"])
@saas_api_only
def apiv1_deativate_account():
    setting = Setting.query.first()
    setting.shop_activated = 0
    database.session.commit()
    return jsonify({"msg": "shop deactivated"})
