from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Query
import uuid

class OrmBase(BaseModel):
    # Common properties across orm models
    # Credit: https://github.com/samuelcolvin/pydantic/issues/1334#issuecomment-679207580

    @validator("*", pre=True)
    def evaluate_lazy_columns(cls, v):
        if isinstance(v, Query):
            return v.all()
        return v

    class Config:
        orm_mode = True


class PlanRequirementsBase(OrmBase):
    created_at: datetime = datetime.utcnow()
    instant_payment: bool
    subscription: bool
    note_to_seller_required: bool
    note_to_buyer_message: Optional[str]


class PlanRequirements(PlanRequirementsBase):
    id: int
    plan_id: int

class PlanRequirementsCreate(PlanRequirementsBase):
    pass


class PlanSellingPointBase(OrmBase):
    created_at: datetime = datetime.utcnow()
    point: str


class PlanSellingPoint(PlanSellingPointBase):
    id: int
    plan_id: int



class PlanSellingPointCreate(PlanSellingPointBase):
    pass

class PlanBase(OrmBase):
    archived: bool = False
    uuid: str = str(uuid.uuid4())
    created_at: datetime = datetime.utcnow()
    title: str
    interval_unit: str = 'monthly'
    interval_amount: int
    sell_price: Optional[int] = 0
    days_before_first_charge: int = 0
    primary_icon: Optional[str]
    requirements: PlanRequirementsBase
    selling_points: List[PlanSellingPointBase]

class Plan(PlanBase):
    id: int

    class Config:
        orm_mode = True


class PlanCreate(PlanBase):
    pass
