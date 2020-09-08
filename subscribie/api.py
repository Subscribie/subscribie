from .auth import token_required
from flask import Blueprint, jsonify, request, Response
from .models import (Plan, PlanRequirements, PlanSellingPoints)
from typing import List
import pydantic
from subscribie import schemas, database
from subscribie.auth import token_required
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

@api.route('/plan/<int:plan_id>', methods=["DELETE"])
@token_required
def delete_plan(plan_id):
    """Delete a plan
    curl -v -X DELETE -H "Authorization: Bearer <token>" http://127.0.0.1:5000/api/plan/229
    """
    plan = Plan.query.get(plan_id)
    # Return 404 if already deleted (archived)
    if plan is None or plan.archived:
        resp = {'msg': f'Plan {plan_id} not found'}
        return jsonify(resp), 404
    else:
        plan.archived = 1
        database.session.commit()

    res = json.loads(schemas.Plan.from_orm(plan).json())
    return jsonify(res), 200

@api.route('/plan/<int:plan_id>', methods=["PUT"])
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
        resp = {'msg': f'Plan {plan_id} not found'}
        return jsonify(resp), 404

    # Perform update
    try:
        plan_in = schemas.PlanUpdate(**request.json).dict(exclude_unset=True)
    except pydantic.error_wrappers.ValidationError as e:
        resp = Response(e.json())
        resp.status_code = 422
        return resp

    for field in plan_in:
        print(field)
        if field == "selling_points":
            selling_points = []
            for selling_point in plan_in[field]:
                selling_points.append(PlanSellingPoints(point=selling_point['point']))
            plan.selling_points = [] # Clear old selling points
            plan.selling_points = selling_points # Overwrite selling points with new values
            continue
        if field == 'requirements':
            plan_requirements = PlanRequirements()
            for key in plan_in[field]:
                setattr(plan_requirements, key, plan_in[field][key])
            plan.requirements = plan_requirements
            continue

        else:
            setattr(plan, field, plan_in[field])

    database.session.commit()

    resp = Response(schemas.Plan.from_orm(plan).json())
    resp.headers['Content-Type'] = 'Application/json'

    return resp, 201


@api.route('/plan', methods=["POST"])
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
