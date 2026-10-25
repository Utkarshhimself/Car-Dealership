import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class VehicleCreate(BaseModel):
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    quantity: int = Field(ge=0)


class VehicleUpdate(BaseModel):
    make: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    quantity: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def contains_update(self) -> "VehicleUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update")
        return self


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    make: str
    model: str
    category: str
    price: Decimal
    quantity: int
    image_filename: str | None
    created_at: datetime
    updated_at: datetime


class VehiclePage(BaseModel):
    items: list[VehicleRead]
    page: int
    page_size: int
    total: int
