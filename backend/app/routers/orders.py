from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..config import get_settings
from ..dependencies import DbSession, current_customer, optional_customer, require_admin
from ..models import CatalogProduct, Customer, InventoryMovement, LoyaltyEntry, Order, ProductVariant
from .catalog import select_variant
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
        # Une référence ne doit jamais permettre de récupérer la commande
        # d'un autre client par simple répétition de la requête.
        raise HTTPException(status_code=409, detail="Cette référence de commande existe déjà")

    product = db.scalar(
        select(CatalogProduct)
        .where(CatalogProduct.id == data.product_id, CatalogProduct.status == "active")
        .options(selectinload(CatalogProduct.variants))
    )
    variant = select_variant(product, data.variant_id) if product else None
    if product is None or variant is None:
        raise HTTPException(status_code=404, detail="Article ou variante introuvable")
    if variant.available_stock <= 0:
        raise HTTPException(status_code=409, detail="Cet article n’est plus disponible")

    order = Order(
        reference=data.reference,
        customer_id=customer.id if customer else None,
        product_id=product.id,
        variant_id=variant.id,
        product_name=product.name,
        displayed_price=variant.selling_price,
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

    if order.variant_id:
        variant = db.scalar(
            select(ProductVariant)
            .where(ProductVariant.id == order.variant_id)
            .with_for_update()
        )
        if variant is None or variant.available_stock <= 0:
            raise HTTPException(status_code=409, detail="Stock insuffisant pour confirmer")
        variant.stock_on_hand -= 1
        db.add(
            InventoryMovement(
                variant_id=variant.id,
                kind="sale",
                quantity_delta=-1,
                stock_after=variant.stock_on_hand,
                note=f"Commande confirmée {order.reference}",
            )
        )

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
