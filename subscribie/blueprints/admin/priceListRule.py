from . import admin
from subscribie.auth import login_required
from subscribie.models import PriceListRule
from flask import render_template, request
import logging
import os

log = logging.getLogger(__name__)

if os.getenv("SUPPORTED_CURRENCIES", False) is not False:
    supported_currencies = []
    for currency in os.getenv("SUPPORTED_CURRENCIES").split(","):
        supported_currencies.append(currency)


@admin.route("/priceListRule", methods=["GET"])
@login_required
def list_priceListRules():
    priceListRules = PriceListRule.query.all()
    return render_template(
        "admin/pricing/priceListRule/list_priceListRules.html",
        priceListRules=priceListRules,
    )


@admin.route("/addPriceListRule", methods=["GET", "POST"])
@login_required
def add_priceListRule():
    return render_template(
        "admin/priceListRule/add_priceListRule.html",
        supported_currencies=supported_currencies,
    )


@admin.route("/editPriceListRule", methods=["GET", "POST"])
@login_required
def edit_priceListRule():
    price_list_id = request.args.get("id")
    price_list = PriceListRule.query.get(price_list_id)

    if request.method == "POST":
        return "TODO save changes"
    else:
        return render_template(
            "admin/priceListRule/edit_priceListRule.html",
            price_list=price_list,
            supported_currencies=supported_currencies,
        )


@admin.route("/deletePriceListRule", methods=["GET", "POST"])
@login_required
def delete_priceListRule():
    return render_template("admin/priceListRule/delete_priceListRule.html")
