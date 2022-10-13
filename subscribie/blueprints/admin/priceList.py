from . import admin
from subscribie.auth import login_required
from subscribie.models import PriceList, PriceListRule
from subscribie.database import database
from flask import render_template, request, url_for, redirect, flash
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
    price_list = PriceList.query.where(PriceList.id == price_list_id).first()
    rules = PriceListRule.query.all()

    if request.method == "POST":
        assignedRules = request.form.getlist("assign")
        assignedRulesList = []
        for assignedRule in assignedRules:
            rule = PriceListRule.query.where(PriceListRule.uuid == assignedRule).first()
            if rule is not None:
                assignedRulesList.append(rule)

        price_list.rules = assignedRulesList
        price_list.name = request.form.get("name")
        if request.form.get("currency") in supported_currencies:
            price_list.currency = request.form.get("currency")

        database.session.commit()
        flash(f'Price list "{request.form.get("name")}" updated.')
        return redirect(url_for("admin.edit_priceList", id=price_list_id))
    else:
        price_list = PriceList.query.get(price_list_id)
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
