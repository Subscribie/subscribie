from .auth import token_required
from flask import Blueprint, jsonify
from .models import (Plan)
from typing import List
from subscribie import schemas
import json

api = Blueprint("api", __name__, url_prefix="/api")

@api.route('/plans')
def get_plans():
    plans = Plan.query.filter_by(archived=0).all()
    res = []
    for plan in plans:
       res.append(json.loads(schemas.Plan.from_orm(plan).json()))
    return jsonify(res)

