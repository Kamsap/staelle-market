from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..dependencies import DbSession
from ..models import CatalogProduct, ProductVariant
from ..schemas import ProductPublicRead


router = APIRouter(prefix="/products", tags=["catalog"])


def public_product(product: CatalogProduct) -> ProductPublicRead | None:
    active_variants = [variant for variant in product.variants if variant.is_active]
    if not active_variants:
        return None
    variant = active_variants[0]
    images = [image.path for image in product.images]
    fallback = "/images/product-nike-bag.svg" if product.brand == "Nike" else "/images/product-adidas-bag.svg"
    return ProductPublicRead(
        id=product.id,
        name=product.name,
        brand=product.brand,
        category=product.category,
        price=variant.selling_price,
        stock=sum(item.available_stock for item in active_variants),
        size=variant.size,
        color=variant.color,
        description=product.description,
        image=images[0] if images else fallback,
        images=images or [fallback],
        featured=product.featured,
    )


@router.get("", response_model=list[ProductPublicRead])
def list_products(db: DbSession) -> list[ProductPublicRead]:
    products = db.scalars(
        select(CatalogProduct)
        .where(CatalogProduct.status == "active")
        .options(
            selectinload(CatalogProduct.variants),
            selectinload(CatalogProduct.images),
        )
        .order_by(CatalogProduct.id)
    ).all()
    return [result for product in products if (result := public_product(product))]


@router.get("/{product_id}", response_model=ProductPublicRead)
def get_product(product_id: int, db: DbSession) -> ProductPublicRead:
    product = db.scalar(
        select(CatalogProduct)
        .where(CatalogProduct.id == product_id, CatalogProduct.status == "active")
        .options(
            selectinload(CatalogProduct.variants),
            selectinload(CatalogProduct.images),
        )
    )
    result = public_product(product) if product else None
    if result is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return result


def select_variant(product: CatalogProduct, variant_id: int | None) -> ProductVariant | None:
    active = [variant for variant in product.variants if variant.is_active]
    if variant_id is None:
        return active[0] if active else None
    return next((variant for variant in active if variant.id == variant_id), None)
