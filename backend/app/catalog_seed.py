import json
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import CatalogProduct, InventoryMovement, ProductImage, ProductVariant


SEED_PATH = Path(__file__).with_name("catalog_seed.json")


def seed_catalog(db: Session) -> int:
    """Importe le catalogue historique une seule fois dans une base vide."""

    if db.scalar(select(func.count(CatalogProduct.id))):
        return 0
    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    for item in data:
        product = CatalogProduct(
            id=item["id"],
            name=item["name"],
            slug=item["slug"],
            brand=item["brand"],
            category=item["category"],
            description=item["description"],
            status=item["status"],
            featured=item["featured"],
        )
        db.add(product)
        db.flush()
        for variant_data in item["variants"]:
            variant = ProductVariant(product_id=product.id, **variant_data)
            db.add(variant)
            db.flush()
            db.add(
                InventoryMovement(
                    variant_id=variant.id,
                    kind="initial",
                    quantity_delta=variant.stock_on_hand,
                    stock_after=variant.stock_on_hand,
                    note="Import du catalogue initial",
                )
            )
        for image_data in item["images"]:
            db.add(ProductImage(product_id=product.id, **image_data))
    db.commit()
    return len(data)
