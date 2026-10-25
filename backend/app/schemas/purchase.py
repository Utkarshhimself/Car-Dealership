"""Request and response schemas for purchases and restocking."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PurchaseCreate(BaseModel):
    quantity: int = Field(gt=0)


class PurchaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    vehicle_id: uuid.UUID
    quantity: int
    unit_price: Decimal
    created_at: datetime


class RestockRequest(BaseModel):
    quantity: int = Field(gt=0)
