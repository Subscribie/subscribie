from . import admin
from subscribie.auth import login_required
from subscribie.models import PriceList
from flask import render_template
import logging
import os

log = logging.getLogger(__name__)


@admin.route("/priceList", methods=["GET"])
@login_required
def list_priceLists():
    priceLists = PriceList.query.all()
    return render_template(
        "admin/priceList/list_priceLists.html", priceLists=priceLists
    )


@admin.route("/addPriceList", methods=["GET", "POST"])
@login_required
def add_priceList():
    if os.getenv("SUPPORTED_CURRENCIES", False) is not False:
        supported_currencies = []
        for currency in os.getenv("SUPPORTED_CURRENCIES").split(","):
            supported_currencies.append(currency)
    return render_template(
        "admin/priceList/add_priceList.html", supported_currencies=supported_currencies
    )


@admin.route("/editPriceList", methods=["GET", "POST"])
@login_required
def edit_priceList():
    return render_template("admin/priceList/edit_priceList.html")


@admin.route("/deletePriceList", methods=["GET", "POST"])
@login_required
def delete_priceList():
    return render_template("admin/priceList/delete_priceList.html")
