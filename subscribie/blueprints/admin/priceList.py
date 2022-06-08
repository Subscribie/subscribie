from . import admin
from subscribie.auth import login_required
from flask import render_template
import logging

log = logging.getLogger(__name__)


@admin.route("/priceList", methods=["GET"])
@login_required
def list_priceLists():
    return render_template("admin/priceList/list_priceLists.html")


@admin.route("/addPriceList", methods=["GET", "POST"])
@login_required
def add_priceList():
    return render_template("admin/priceList/add_priceList.html")
