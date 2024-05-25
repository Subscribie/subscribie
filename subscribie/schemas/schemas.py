from pydantic import field_validator, ConfigDict, BaseModel
from enum import Enum
import datetime
from typing import List, Optional
from sqlalchemy.orm import Query
import uuid as _uuid


class OrmBase(BaseModel):
    # Common properties across orm models
    # Credit: https://github.com/samuelcolvin/pydantic/issues/1334#issuecomment-679207580 # noqa

    @field_validator("*", mode="before")
    @classmethod
    def evaluate_lazy_columns(cls, v):
        if isinstance(v, Query):
            return v.all()
        return v

    model_config = ConfigDict(from_attributes=True)


class PlanRequirementsBase(OrmBase):
    created_at: datetime.datetime
    instant_payment: bool
    subscription: bool
    note_to_seller_required: Optional[bool] = None
    note_to_buyer_message: Optional[str] = None


class PlanRequirements(PlanRequirementsBase):
    id: int
    plan_id: int


class PlanRequirementsCreate(PlanRequirementsBase):
    pass


class PlanSellingPointBase(OrmBase):
    created_at: datetime.datetime
    point: str


class PlanSellingPoint(PlanSellingPointBase):
    id: int
    plan_id: int


class PlanSellingPointCreate(PlanSellingPointBase):
    pass


class IntervalUnitEnum(str, Enum):
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class PlanBase(OrmBase):
    title: Optional[str] = None
    requirements: Optional[PlanRequirementsBase] = None
    selling_points: Optional[List[PlanSellingPointBase]] = []
    archived: Optional[bool] = False
    uuid: str = str(_uuid.uuid4())
    description: str
    interval_unit: Optional[IntervalUnitEnum] = "monthly"
    interval_amount: Optional[int] = None
    sell_price: Optional[int] = 0
    days_before_first_charge: Optional[int] = 0
    primary_icon: Optional[str] = ""


class PlanInDBBase(PlanBase):
    created_at: datetime.datetime


class Plan(PlanBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class PlanUpdate(PlanBase):
    pass


class PlanCreate(PlanBase):
    title: str
    created_at: datetime.datetime


class Company(OrmBase):
    name: str


class ShopBase(OrmBase):
    version: int
    users: List[str]
    password: Optional[str] = None
    login_token: Optional[str] = None
    company: Company
    plans: Optional[List[Plan]] = []


class ShopCreate(ShopBase):
    pass


class Shop(ShopBase):
    pass
