from . import admin
from subscribie.auth import login_required
from subscribie.models import PriceList, PriceListRule
from flask import render_template, request
import logging
import os

log = logging.getLogger(__name__)

if os.getenv("SUPPORTED_CURRENCIES", False) is not False:
    supported_currencies = []
    for currency in os.getenv("SUPPORTED_CURRENCIES").split(","):
        supported_currencies.append(currency)


@admin.route("/priceList", methods=["GET"])
@login_required
def list_priceLists():
    priceLists = PriceList.query.all()
    return render_template(
        "admin/pricing/priceList/list_priceLists.html", priceLists=priceLists
    )


@admin.route("/addPriceList", methods=["GET", "POST"])
@login_required
def add_priceList():
    return render_template(
        "admin/pricing/priceList/add_priceList.html",
        supported_currencies=supported_currencies,
    )


@admin.route("/editPriceList", methods=["GET", "POST"])
@login_required
def edit_priceList():
    price_list_id = request.args.get("id")
    price_list = PriceList.query.get(price_list_id)
    rules = PriceListRule.query.all()

    if request.method == "POST":
        return "TODO save changes"
    else:
        return render_template(
            "admin/pricing/priceList/edit_priceList.html",
            price_list=price_list,
            supported_currencies=supported_currencies,
            rules=rules,
        )


@admin.route("/deletePriceList", methods=["GET", "POST"])
@login_required
def delete_priceList():
    return render_template("admin/pricing/priceList/delete_priceList.html")
