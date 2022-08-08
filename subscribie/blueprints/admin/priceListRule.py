from . import admin
from subscribie.auth import login_required
from subscribie.models import PriceListRule
from subscribie.database import database
from flask import render_template, request, redirect, url_for, flash
import logging
import os
from datetime import datetime

dog = 1
log = logging.getLogger(__name__)

if os.getenv("SUPPORTED_CURRENCIES", False) is not False:
    supported_currencies = []
    for currency in os.getenv("SUPPORTED_CURRENCIES").split(","):
        supported_currencies.append(currency)


@admin.route("/priceListRule", methods=["GET"])
@login_required
def list_priceListRules():
    priceListRules = PriceListRule.query.filter(
        PriceListRule.active != False  # noqa: E712
    ).all()

    confirm = False
    if "confirm" in request.args:
        confirm = request.args.get("confirm")
        if confirm == "true":
            confirm = True

    return render_template(
        "admin/pricing/priceListRule/list_priceListRules.html",
        priceListRules=priceListRules,
    )


@admin.route("/addPriceListRule", methods=["GET", "POST"])
@login_required
def add_priceListRule():
    if request.method == "POST":
        affects_sell_price = request.form.get("affects_sell_price", False)
        if affects_sell_price == "on":
            affects_sell_price = True

        affects_interval_amount = request.form.get(
            "affects_interval_amount", False
        )  # noqa: E501
        if affects_interval_amount == "on":
            affects_interval_amount = True

        percent_discount = request.form.get("percent_discount", None)
        percent_increase = request.form.get("percent_increase", None)
        amount_discount = request.form.get("amount_discount", None)
        amount_increase = request.form.get("amount_increase", None)
        min_sell_price = request.form.get("min_sell_price", None)
        min_interval_amount = request.form.get("min_interval_amount", None)

        # Create PriceListRule
        priceListRuleForm = dict(request.form)
        priceListRuleForm["percent_discount"] = percent_discount
        priceListRuleForm["percent_increase"] = percent_increase
        priceListRuleForm["amount_discount"] = amount_discount
        priceListRuleForm["amount_increase"] = amount_increase
        priceListRuleForm["min_sell_price"] = min_sell_price
        priceListRuleForm["min_interval_amount"] = min_interval_amount
        priceListRuleForm["start_date"] = datetime.now()
        priceListRuleForm["expire_date"] = datetime.now()
        priceListRuleForm["affects_sell_price"] = affects_sell_price
        priceListRuleForm["affects_interval_amount"] = affects_interval_amount
        priceListRule = PriceListRule(**priceListRuleForm)
        database.session.add(priceListRule)
        database.session.commit()

        flash(f'Price list rule added: "{priceListRule.name}"')
        return redirect(url_for("admin.list_priceListRules"))
    else:
        return render_template(
            "admin/pricing/priceListRule/add_priceListRule.html",
            supported_currencies=supported_currencies,
        )


@admin.route("/editPriceListRule", methods=["GET", "POST"])
@login_required
def edit_priceListRule():
    priceListRuleId = request.args.get("id")
    priceListRule = PriceListRule.query.where(
        PriceListRule.uuid == priceListRuleId
    ).first()

    if request.method == "POST":
        priceListRuleForm = dict(request.form)

        if "affects_sell_price" not in priceListRuleForm:
            priceListRuleForm["affects_sell_price"] = False
        else:
            priceListRuleForm["affects_sell_price"] = True

        if "affects_interval_amount" not in priceListRuleForm:
            priceListRuleForm["affects_interval_amount"] = False
        else:
            priceListRuleForm["affects_interval_amount"] = True

        priceListRuleForm["start_date"] = datetime.now()
        priceListRuleForm["expire_date"] = datetime.now()
        priceListRule = PriceListRule.query.where(
            PriceListRule.uuid == priceListRuleId
        )  # noqa
        priceListRule.update(priceListRuleForm)
        database.session.commit()
        flash(f'Price list rule "{priceListRuleForm["name"]}" updated')
        return redirect(url_for("admin.list_priceListRules"))
    else:
        return render_template(
            "admin/pricing/priceListRule/edit_priceListRule.html",
            priceListRule=priceListRule,
            supported_currencies=supported_currencies,
        )


@admin.route("/deletePriceListRule")
@login_required
def delete_priceListRule():
    priceListRules = PriceListRule.query.all()
    priceListRule = None

    confirm = False
    if "confirm" in request.args:
        confirm = request.args.get("confirm")
        if confirm == "true":
            confirm = True
            uuid = request.args.get("id")
            priceListRule = PriceListRule.query.filter_by(uuid=uuid).first()

    return render_template(
        "admin/pricing/priceListRule/list_priceListRules.html",
        priceListRules=priceListRules,
        confirm=confirm,
        priceListRule=priceListRule,
    )


@admin.route("/priceListRule/delete/<uuid>", methods=["GET", "POST"])
@login_required
def delete_priceListRule_by_uuid(uuid):
    """Mark inactive (dont actually delete) priceListRule"""
    priceListRule = PriceListRule.query.filter_by(uuid=uuid).first()

    if uuid is not False:
        # Perform archive
        priceListRule.active = False
        database.session.commit()
    flash("Price list rule deleted.")
    return redirect(url_for("admin.list_priceListRules"))
