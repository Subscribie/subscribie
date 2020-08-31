from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Query

class OrmBase(BaseModel):
    # Common properties across orm models
    # Credit: https://github.com/samuelcolvin/pydantic/issues/1334#issuecomment-679207580
    id: int

    @validator("*", pre=True)
    def evaluate_lazy_columns(cls, v):
        if isinstance(v, Query):
            return v.all()
        return v

    class Config:
        orm_mode = True


class PlanRequirements(OrmBase):
    id: int
    created_at: datetime
    plan_id: int
    instant_payment: bool
    subscription: bool
    note_to_seller_required: bool
    note_to_buyer_message: str

class PlanSellingPoint(OrmBase):
    id: int
    created_at: datetime
    point: str
    plan_id: int

class Plan(OrmBase):
    id: int
    created_at: datetime
    archived: bool
    uuid: str
    title: str
    interval_unit: str
    interval_amount: int
    sell_price: int
    days_before_first_charge: int
    primary_icon: Optional[str]
    requirements: PlanRequirements
    selling_points: List[PlanSellingPoint]

    class Config:
        orm_mode = True

