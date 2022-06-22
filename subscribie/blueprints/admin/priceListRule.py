from . import admin
from subscribie.auth import login_required
from subscribie.models import PriceListRule
from subscribie.database import database
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
    if request.method == "POST":
        name = request.form.get("name", None)  # noqa: F841
        start_date = request.form.get("start_date", None)  # noqa: F841
        expire_date = request.form.get("expire_date", None)  # noqa: F841
        affects_sell_price = request.form.get("affects_sell_price", None)  # noqa: F841
        affects_interval_amount = request.form.get(  # noqa: F841
            "affects_interval_amount", None
        )
        percent_discount = request.form.get("percent_discount", None)  # noqa: F841
        percent_increase = request.form.get("percent_increase", None)  # noqa: F841
        amount_discount = request.form.get("amount_discount", None)  # noqa: F841
        amount_increase = request.form.get("amount_increase", None)  # noqa: F841
        min_sell_price = request.form.get("min_sell_price", None)  # noqa: F841
        min_interval_amount = request.form.get(  # noqa: F841
            "min_interval_amount", None
        )

        # Create PriceListRule
        priceListRule = PriceListRule(**dict(request.form))
        database.session.add(priceListRule)
        database.session.commit()

        return request.data
    else:
        return render_template(
            "admin/pricing/priceListRule/add_priceListRule.html",
            supported_currencies=supported_currencies,
        )


@admin.route("/editPriceListRule", methods=["GET", "POST"])
@login_required
def edit_priceListRule():
    priceListRuleId = request.args.get("id")
    priceListRule = PriceListRule.query.where(uuid=priceListRuleId)

    if request.method == "POST":
        return "TODO save changes"
    else:
        return render_template(
            "admin/pricing/priceListRule/edit_priceListRule.html",
            priceListRule=priceListRule,
            supported_currencies=supported_currencies,
        )


@admin.route("/deletePriceListRule", methods=["GET", "POST"])
@login_required
def delete_priceListRule():
    return render_template("admin/priceListRule/delete_priceListRule.html")
