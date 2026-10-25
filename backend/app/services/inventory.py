"""Transactional inventory workflows."""

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models.purchase import Purchase
from app.models.vehicle import Vehicle


class VehicleNotFoundError(Exception):
    """Raised when an inventory operation targets a missing vehicle."""


class InsufficientStockError(Exception):
    """Raised when the requested purchase quantity is unavailable."""


def purchase_vehicle(
    db: Session, *, user_id: uuid.UUID, vehicle_id: uuid.UUID, quantity: int
) -> Purchase:
    """Atomically decrement stock and persist the purchase at the current unit price."""
    try:
        result = db.execute(
            update(Vehicle)
            .where(Vehicle.id == vehicle_id, Vehicle.quantity >= quantity)
            .values(quantity=Vehicle.quantity - quantity, updated_at=func.now())
            .returning(Vehicle.price)
        )
        unit_price = result.scalar_one_or_none()

        if unit_price is None:
            exists = db.scalar(select(Vehicle.id).where(Vehicle.id == vehicle_id))
            db.rollback()
            if exists is None:
                raise VehicleNotFoundError
            raise InsufficientStockError

        purchase = Purchase(
            user_id=user_id,
            vehicle_id=vehicle_id,
            quantity=quantity,
            unit_price=unit_price,
        )
        db.add(purchase)
        db.commit()
        db.refresh(purchase)
        return purchase
    except Exception:
        db.rollback()
        raise


def restock_vehicle(db: Session, *, vehicle_id: uuid.UUID, quantity: int) -> Vehicle:
    """Atomically add stock and return the updated vehicle."""
    try:
        vehicle = db.execute(
            update(Vehicle)
            .where(Vehicle.id == vehicle_id)
            .values(quantity=Vehicle.quantity + quantity, updated_at=func.now())
            .returning(Vehicle)
        ).scalar_one_or_none()

        if vehicle is None:
            db.rollback()
            raise VehicleNotFoundError

        db.commit()
        db.refresh(vehicle)
        return vehicle
    except Exception:
        db.rollback()
        raise
