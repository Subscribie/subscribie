import logging
from .auth import token_required, login_required
from flask import Blueprint, jsonify, request, Response, redirect, url_for
from .models import Plan, PlanRequirements, PlanSellingPoints, User, Setting
from .auth import generate_login_url
from .auth import get_magic_login_link
import pydantic
from subscribie import schemas, database
import json
import secrets
from Crypto.Cipher import AES
import os
import base64

log = logging.getLogger(__name__)
api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/shop-name-taken/<shop_name>", methods=["GET"])
def shop_name_taken(shop_name):
    """Check if shop name has been taken or not"""
    from builder import Shop

    shop_name = f"https://{shop_name}.{os.getenv('SUBSCRIBIE_DOMAIN')}"
    lookup = database.session.query(Shop).where(Shop.site_url == shop_name).all()
    log.debug(f"Running shop_name_taken lookup for: {lookup}")
    if len(lookup) == 0:
        log.debug(f"Shop name not taken: {lookup}")
        return jsonify(False)
    log.debug(f"Shop name is already taken: {lookup}")
    return jsonify(True)


@api.route("/magic-login-link", methods=["POST"])
def api_get_magic_login_link():
    email = request.form.get("email", None)
    if email is not None:
        user = User.query.filter_by(email=email).first()
    if user is not None:
        login_url = generate_login_url(email)
        resp = {"login_url": login_url}
        return resp
    return {"msg": "Could not generate login url"}


@api.route("/get-login-link", methods=["POST"])
def get_login_link():
    email = request.form.get("email", None)
    password = request.form.get("password", None)
    try:
        login_link = get_magic_login_link(email, password)
        return login_link
    except Exception as e:
        log.error(f"Could not get_login_link: {e}")
        return {"msg": "Could not generate login link"}


def encrypt_secret(data=None, key=os.getenv("SECRET_KEY")):
    assert data is not None
    data = data.encode("utf-8")
    key = key[:16].encode("utf-8")
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce, ciphertext, tag


def decrypt_secret(data, key=os.getenv("SECRET_KEY")):
    nonce = base64.b64decode(data.split(":")[0])
    ciphertext = base64.b64decode(data.split(":")[1])
    tag = base64.b64decode(data.split(":")[2])
    key = key[:16].encode("utf-8")
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    cipher.verify(tag)

    return plaintext


def save_api_key(api_key, mode):
    setting = Setting.query.first()
    nonce, ciphertext, tag = encrypt_secret(data=api_key)

    nonce = base64.b64encode(nonce).decode("utf-8")
    ciphertext = base64.b64encode(ciphertext).decode("utf-8")
    tag = base64.b64encode(tag).decode("utf-8")
    if mode == "test":
        setting.api_key_secret_test = f"{nonce}:{ciphertext}:{tag}"
        api_key = setting.api_key_secret_test
    elif mode == "live":
        setting.api_key_secret_live = f"{nonce}:{ciphertext}:{tag}"
        api_key = setting.api_key_secret_live

    database.session.commit()

    return api_key


@api.route("/generate-test-api-key", methods=["GET"])
@api.route("/generate-live-api-key", methods=["GET"])
@login_required
def apiv1_generate_api_key():
    setting = Setting.query.first()
    if "test" in request.path:
        # Generate api key
        api_key = f"subscribie_test_{secrets.token_urlsafe(255)}"
        # Store api key
        save_api_key(api_key, mode="test")

    elif "live" in request.path:
        # Generate api key
        api_key = f"subscribie_live_{secrets.token_urlsafe(255)}"
        # Store api key
        save_api_key(api_key, mode="live")
        # Decrypt
        decrypt_secret(data=setting.api_key_secret_live)

    if "live" in request.path:
        return redirect("/api/fetch-live-api-key")
    elif "test" in request.path:
        return redirect("/api/fetch-test-api-key")


@api.route("/fetch-test-api-key", methods=["GET"])
@api.route("/fetch-live-api-key", methods=["GET"])
@login_required
def apiv1_fetch_api_key():
    setting = Setting.query.first()
    if "test" in request.path:
        api_key = decrypt_secret(data=setting.api_key_secret_test)
    elif "live" in request.path:
        api_key = decrypt_secret(data=setting.api_key_secret_live)

    return jsonify(api_key.decode("utf-8"))


@api.route("/plans")
def get_plans():
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    res = []
    for plan in plans:
        res.append(json.loads(schemas.Plan.from_orm(plan).json()))
    return jsonify(res)


@api.route("/plan/<int:plan_id>")
def get_plan(plan_id):
    plan = Plan.query.get(plan_id)
    res = json.loads(schemas.Plan.from_orm(plan).json())
    res["url"] = url_for("views.view_plan", uuid=plan.uuid, _external=True)
    return jsonify(res)


@api.route("/plan/<int:plan_id>", methods=["DELETE"])
@token_required
def delete_plan(plan_id):
    """Delete a plan
    curl -v -X DELETE \
        -H "Authorization: Bearer <token>" \
        http://127.0.0.1:5000/api/plan/229
    """
    plan = Plan.query.get(plan_id)
    # Return 404 if already deleted (archived)
    if plan is None or plan.archived:
        resp = {"msg": f"Plan {plan_id} not found"}
        return jsonify(resp), 404
    else:
        plan.archived = 1
        database.session.commit()

    res = json.loads(schemas.Plan.from_orm(plan).json())
    return jsonify(res), 200


@api.route("/plan/<int:plan_id>", methods=["PUT"])
@token_required
def update_plan(plan_id):
    """Update a plan
    Example PUT request:

    curl -v -H 'Content-Type: application/json' -H "Authorization: Bearer <token>"
    -X PUT
    -d '
    {
      "title":"Coffee",
      "interval_unit": "monthly",
      "selling_points": [
        {"point":"Quality"},
        {"point": "Unique blend"}
      ],
      "interval_amount":888,
      "requirements": {
        "instant_payment": false,
        "subscription": true,
        "note_to_seller_required": false}
    }'
    http://127.0.0.1:5000/api/plan/229
    """
    plan = Plan.query.get(plan_id)
    if plan is None:
        resp = {"msg": f"Plan {plan_id} not found"}
        return jsonify(resp), 404
    log.info(f"Updating plan {plan_id}")

    # Perform update
    try:
        plan_in = schemas.PlanUpdate(**request.json).dict(exclude_unset=True)
    except pydantic.error_wrappers.ValidationError as e:
        resp = Response(e.json())
        resp.status_code = 422
        return resp

    for field in plan_in:
        if field == "selling_points":
            selling_points = []
            for selling_point in plan_in[field]:
                selling_points.append(PlanSellingPoints(point=selling_point["point"]))
            plan.selling_points = []  # Clear old selling points
            plan.selling_points = (
                selling_points  # Overwrite selling points with new values
            )
            continue
        if field == "requirements":
            plan_requirements = PlanRequirements()
            for key in plan_in[field]:
                setattr(plan_requirements, key, plan_in[field][key])
            plan.requirements = plan_requirements
            continue

        else:
            setattr(plan, field, plan_in[field])

    database.session.commit()

    resp = Response(schemas.Plan.from_orm(plan).json())
    resp.headers["Content-Type"] = "Application/json"

    return resp, 201


@api.route("/plan", methods=["POST"])
@token_required
def create_plan():
    """
    Example post request:
    curl -v -H "Content-Type: application/json"
    -H "Authorization: Bearer <token>" -d '
    {
      "interval_unit": "monthly",
      "interval_amount": "599",
      "sell_price": 0,
      "title": "My title",
      "requirements": {
        "instant_payment": false,
        "subscription": true,
        "note_to_seller_required": false
      },
      "selling_points": [
        {"point":"Quality"}
      ]
    }' http://127.0.0.1:5000/api/plan
    """
    try:
        planData = schemas.PlanCreate(**request.json)
        plan = Plan()
        database.session.add(plan)
        for field in planData:
            if type(field[1]) == list:
                for sellingPoint in field[1]:
                    plan.selling_points.append(
                        PlanSellingPoints(point=sellingPoint.point)
                    )
                continue
            if isinstance(field[1], pydantic.BaseModel):
                if field[0] == "requirements":
                    plan_requirements = PlanRequirements()
                    for attr in field[1]:
                        setattr(plan_requirements, attr[0], attr[1])
                    plan.requirements = plan_requirements
                continue
            setattr(plan, field[0], field[1])
    except pydantic.error_wrappers.ValidationError as e:
        resp = Response(e.json())
        resp.status_code = 422
        return resp

    database.session.commit()

    resp = Response(schemas.Plan.from_orm(plan).json())
    resp.headers["Content-Type"] = "Application/json"

    return resp, 201
