from .auth import token_required
from flask import Blueprint, jsonify, request, Response
from .models import (Plan, PlanRequirements, PlanSellingPoints)
from typing import List
import pydantic
from subscribie import schemas, database
import json

api = Blueprint("api", __name__, url_prefix="/api")

@api.route('/plans')
def get_plans():
    plans = Plan.query.filter_by(archived=0).all()
    res = []
    for plan in plans:
       res.append(json.loads(schemas.Plan.from_orm(plan).json()))
    return jsonify(res)

@api.route('/plan/<int:plan_id>')
def get_plan(plan_id):
    plan = Plan.query.get(plan_id)
    res = json.loads(schemas.Plan.from_orm(plan).json())
    return jsonify(res)

@api.route('/plan', methods=["POST"])
def create_plan():
    """
    Example post request:
    curl -v -H "Content-Type: application/json" -d '
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
                    plan.selling_points.append(PlanSellingPoints(point=sellingPoint.point))
                continue
            if isinstance(field[1], pydantic.BaseModel):
                if field[0] == 'requirements':
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
    resp.headers['Content-Type'] = 'Application/json'

    return resp, 201
