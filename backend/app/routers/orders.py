from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from ..config import get_settings
from ..dependencies import DbSession, current_customer, optional_customer, require_admin
from ..models import Customer, LoyaltyEntry, Order
from ..schemas import OrderConfirm, OrderCreate, OrderRead


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate,
    db: DbSession,
    customer: Annotated[Customer | None, Depends(optional_customer)],
) -> Order:
    existing = db.scalar(select(Order).where(Order.reference == data.reference))
    if existing:
        return existing

    order = Order(
        reference=data.reference,
        customer_id=customer.id if customer else None,
        product_id=data.product_id,
        product_name=data.product_name,
        displayed_price=data.displayed_price,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/mine", response_model=list[OrderRead])
def my_orders(
    db: DbSession,
    customer: Annotated[Customer, Depends(current_customer)],
) -> list[Order]:
    return list(
        db.scalars(
            select(Order).where(Order.customer_id == customer.id).order_by(Order.created_at.desc())
        )
    )


@router.post("/{order_id}/confirm", response_model=OrderRead, dependencies=[Depends(require_admin)])
def confirm_order(order_id: int, data: OrderConfirm, db: DbSession) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    if order.status == "confirmed":
        raise HTTPException(status_code=409, detail="Commande déjà confirmée")

    order.status = "confirmed"
    order.amount_paid = data.amount_paid
    order.confirmed_at = datetime.now(timezone.utc)

    if order.customer_id:
        points = data.amount_paid // get_settings().points_per_xaf
        customer = db.get(Customer, order.customer_id)
        if customer and points > 0:
            customer.points += points
            order.points_earned = points
            db.add(
                LoyaltyEntry(
                    customer_id=customer.id,
                    order=order,
                    points=points,
                    reason=f"Commande {order.reference}",
                )
            )

    db.commit()
    db.refresh(order)
    return order
