"""Authenticated vehicle inventory endpoints."""

import uuid
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select

from app.api.dependencies import CurrentUser, DbSession, require_admin
from app.models.vehicle import Vehicle
from app.schemas.purchase import PurchaseCreate, PurchaseRead, RestockRequest
from app.schemas.vehicle import VehicleCreate, VehiclePage, VehicleRead, VehicleUpdate
from app.services.inventory import (
    InsufficientStockError,
    VehicleNotFoundError,
    purchase_vehicle,
    restock_vehicle,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=VehiclePage)
def list_vehicles(
    _: CurrentUser,
    db: DbSession,
    make: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    model: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    category: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    min_price: Annotated[Decimal | None, Query(gt=0, max_digits=12, decimal_places=2)] = None,
    max_price: Annotated[Decimal | None, Query(gt=0, max_digits=12, decimal_places=2)] = None,
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    in_stock: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> VehiclePage:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="min_price cannot exceed max_price",
        )

    filters = []
    if make is not None:
        filters.append(Vehicle.make.ilike(f"%{make.strip()}%"))
    if model is not None:
        filters.append(Vehicle.model.ilike(f"%{model.strip()}%"))
    if category is not None:
        filters.append(Vehicle.category.ilike(f"%{category.strip()}%"))
    if min_price is not None:
        filters.append(Vehicle.price >= min_price)
    if max_price is not None:
        filters.append(Vehicle.price <= max_price)
    if in_stock is True:
        filters.append(Vehicle.quantity > 0)
    if in_stock is False:
        filters.append(Vehicle.quantity == 0)
    if q is not None:
        pattern = f"%{q.strip()}%"
        filters.append(
            or_(
                Vehicle.make.ilike(pattern),
                Vehicle.model.ilike(pattern),
                Vehicle.category.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(Vehicle).where(*filters)) or 0
    statement = (
        select(Vehicle)
        .where(*filters)
        .order_by(Vehicle.created_at.desc(), Vehicle.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    vehicles = list(db.scalars(statement))
    return VehiclePage(items=vehicles, page=page, page_size=page_size, total=total)


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: uuid.UUID, _: CurrentUser, db: DbSession) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return vehicle


@router.post(
    "",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_vehicle(payload: VehicleCreate, db: DbSession) -> Vehicle:
    vehicle = Vehicle(**payload.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.patch(
    "/{vehicle_id}",
    response_model=VehicleRead,
    dependencies=[Depends(require_admin)],
)
def update_vehicle(vehicle_id: uuid.UUID, payload: VehicleUpdate, db: DbSession) -> Vehicle:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def delete_vehicle(vehicle_id: uuid.UUID, db: DbSession) -> None:
    vehicle = db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")

    db.delete(vehicle)
    db.commit()


@router.post(
    "/{vehicle_id}/purchase",
    response_model=PurchaseRead,
    status_code=status.HTTP_201_CREATED,
)
def purchase(
    vehicle_id: uuid.UUID,
    payload: PurchaseCreate,
    current_user: CurrentUser,
    db: DbSession,
) -> PurchaseRead:
    try:
        return purchase_vehicle(
            db,
            user_id=current_user.id,
            vehicle_id=vehicle_id,
            quantity=payload.quantity,
        )
    except VehicleNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found") from error
    except InsufficientStockError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insufficient vehicle stock",
        ) from error


@router.post(
    "/{vehicle_id}/restock",
    response_model=VehicleRead,
    dependencies=[Depends(require_admin)],
)
def restock(vehicle_id: uuid.UUID, payload: RestockRequest, db: DbSession) -> Vehicle:
    try:
        return restock_vehicle(db, vehicle_id=vehicle_id, quantity=payload.quantity)
    except VehicleNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found") from error
