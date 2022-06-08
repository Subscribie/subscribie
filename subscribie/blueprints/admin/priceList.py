from . import admin
from subscribie.auth import login_required
from flask import render_template
import logging

log = logging.getLogger(__name__)


@admin.route("/priceList", methods=["GET", "POST"])
@login_required
def list_priceLists():
    return render_template("admin/priceList/priceLists.html")
