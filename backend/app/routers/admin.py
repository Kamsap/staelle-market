import json
from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Header, HTTPException, Response, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..config import get_settings
from ..dependencies import (
    ADMIN_COOKIE_NAME,
    DbSession,
    current_admin,
    require_trusted_admin_origin,
)
from ..models import (
    AdminUser,
    AuditLog,
    CatalogProduct,
    InventoryMovement,
    Order,
    ProductImage,
    ProductVariant,
)
from ..schemas import (
    AdminBootstrap,
    AdminDashboardRead,
    AdminLogin,
    AdminRead,
    InventoryMovementRead,
    ProductAdminRead,
    ProductWrite,
    StockAdjustment,
    UploadRead,
)
from ..security import create_admin_access_token, hash_password, verify_password


router = APIRouter(
    prefix="/admin",
    tags=["administration"],
    dependencies=[Depends(require_trusted_admin_origin)],
)


def audit(
    db: DbSession,
    admin: AdminUser | None,
    action: str,
    entity_type: str,
    entity_id: int | None,
    details: dict[str, object] | None = None,
) -> None:
    db.add(
        AuditLog(
            admin_user_id=admin.id if admin else None,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=json.dumps(details or {}, ensure_ascii=False),
        )
    )


def product_query():
    return select(CatalogProduct).options(
        selectinload(CatalogProduct.variants),
        selectinload(CatalogProduct.images),
    )


def ensure_unique_product_fields(
    db: DbSession, data: ProductWrite, product_id: int | None = None
) -> None:
    slug_owner = db.scalar(select(CatalogProduct).where(CatalogProduct.slug == data.slug))
    if slug_owner and slug_owner.id != product_id:
        raise HTTPException(status_code=409, detail="Ce nom d’URL est déjà utilisé")

    skus = [variant.sku.strip().upper() for variant in data.variants]
    if len(skus) != len(set(skus)):
        raise HTTPException(status_code=409, detail="Chaque variante doit avoir un SKU unique")
    existing = db.scalars(select(ProductVariant).where(ProductVariant.sku.in_(skus))).all()
    for variant in existing:
        if product_id is None or variant.product_id != product_id:
            raise HTTPException(status_code=409, detail=f"Le SKU {variant.sku} existe déjà")


def set_product_fields(product: CatalogProduct, data: ProductWrite) -> None:
    product.name = data.name.strip()
    product.slug = data.slug.strip().lower()
    product.brand = data.brand.strip()
    product.category = data.category.strip()
    product.description = data.description.strip()
    product.status = data.status
    product.featured = data.featured


def replace_images(product: CatalogProduct, data: ProductWrite) -> None:
    product.images.clear()
    product.images.extend(
        ProductImage(
            path=image.path.strip(),
            alt_text=image.alt_text.strip() or product.name,
            position=index,
        )
        for index, image in enumerate(sorted(data.images, key=lambda item: item.position))
    )


@router.post("/auth/bootstrap", response_model=AdminRead, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(
    data: AdminBootstrap,
    db: DbSession,
    x_admin_key: str | None = Header(default=None),
) -> AdminUser:
    if x_admin_key != get_settings().admin_api_key:
        raise HTTPException(status_code=403, detail="Clé d’initialisation invalide")
    if db.scalar(select(func.count(AdminUser.id))):
        raise HTTPException(status_code=409, detail="Un administrateur existe déjà")
    admin = AdminUser(
        full_name=data.full_name.strip(),
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        role="owner",
    )
    db.add(admin)
    db.flush()
    audit(db, admin, "admin.bootstrap", "admin_user", admin.id)
    db.commit()
    db.refresh(admin)
    return admin


@router.post("/auth/login", response_model=AdminRead)
def login_admin(data: AdminLogin, response: Response, db: DbSession) -> AdminUser:
    admin = db.scalar(select(AdminUser).where(AdminUser.email == data.email.lower()))
    if admin is None or not admin.is_active or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou mot de passe incorrect")
    settings = get_settings()
    response.set_cookie(
        key=ADMIN_COOKIE_NAME,
        value=create_admin_access_token(admin.id, admin.role),
        max_age=settings.admin_access_token_minutes * 60,
        httponly=True,
        secure=settings.app_env.lower() == "production",
        samesite="lax",
        path="/api/v1/admin",
    )
    return admin


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_admin(response: Response) -> None:
    response.delete_cookie(ADMIN_COOKIE_NAME, path="/api/v1/admin")


@router.get("/auth/me", response_model=AdminRead)
def admin_me(admin: AdminUser = Depends(current_admin)) -> AdminUser:
    return admin


@router.get("/dashboard", response_model=AdminDashboardRead)
def dashboard(db: DbSession, _admin: AdminUser = Depends(current_admin)) -> AdminDashboardRead:
    active_products = db.scalar(
        select(func.count(CatalogProduct.id)).where(CatalogProduct.status == "active")
    ) or 0
    total_stock = db.scalar(
        select(func.coalesce(func.sum(ProductVariant.stock_on_hand - ProductVariant.stock_reserved), 0))
        .join(CatalogProduct)
        .where(CatalogProduct.status == "active", ProductVariant.is_active.is_(True))
    ) or 0
    low_stock = db.scalar(
        select(func.count(ProductVariant.id))
        .join(CatalogProduct)
        .where(
            CatalogProduct.status == "active",
            ProductVariant.is_active.is_(True),
            ProductVariant.stock_on_hand - ProductVariant.stock_reserved
            <= ProductVariant.low_stock_threshold,
        )
    ) or 0
    pending_orders = db.scalar(select(func.count(Order.id)).where(Order.status == "pending")) or 0
    revenue = db.scalar(
        select(func.coalesce(func.sum(Order.amount_paid), 0)).where(Order.status == "confirmed")
    ) or 0
    return AdminDashboardRead(
        active_products=int(active_products),
        total_available_stock=int(total_stock),
        low_stock_variants=int(low_stock),
        pending_orders=int(pending_orders),
        confirmed_revenue=int(revenue),
    )


@router.get("/products", response_model=list[ProductAdminRead])
def admin_products(db: DbSession, _admin: AdminUser = Depends(current_admin)) -> list[CatalogProduct]:
    return list(db.scalars(product_query().order_by(CatalogProduct.updated_at.desc())))


@router.post("/products", response_model=ProductAdminRead, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductWrite,
    db: DbSession,
    admin: AdminUser = Depends(current_admin),
) -> CatalogProduct:
    ensure_unique_product_fields(db, data)
    product = CatalogProduct()
    set_product_fields(product, data)
    db.add(product)
    db.flush()
    for item in data.variants:
        variant = ProductVariant(
            sku=item.sku.strip().upper(),
            size=item.size.strip() if item.size else None,
            color=item.color.strip() if item.color else None,
            selling_price=item.selling_price,
            compare_at_price=item.compare_at_price,
            cost_price=item.cost_price,
            stock_on_hand=item.stock_on_hand,
            stock_reserved=item.stock_reserved,
            low_stock_threshold=item.low_stock_threshold,
            is_active=item.is_active,
        )
        product.variants.append(variant)
        db.flush()
        db.add(
            InventoryMovement(
                variant_id=variant.id,
                admin_user_id=admin.id,
                kind="initial",
                quantity_delta=item.stock_on_hand,
                stock_after=item.stock_on_hand,
                note="Stock initial de l’article",
            )
        )
    replace_images(product, data)
    audit(db, admin, "product.create", "product", product.id, {"name": product.name})
    db.commit()
    return db.scalar(product_query().where(CatalogProduct.id == product.id))


@router.put("/products/{product_id}", response_model=ProductAdminRead)
def update_product(
    product_id: int,
    data: ProductWrite,
    db: DbSession,
    admin: AdminUser = Depends(current_admin),
) -> CatalogProduct:
    product = db.scalar(product_query().where(CatalogProduct.id == product_id))
    if product is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    ensure_unique_product_fields(db, data, product_id)
    set_product_fields(product, data)

    existing = {variant.id: variant for variant in product.variants}
    retained: set[int] = set()
    for item in data.variants:
        if item.id:
            variant = existing.get(item.id)
            if variant is None:
                raise HTTPException(status_code=400, detail="Variante invalide pour cet article")
            retained.add(variant.id)
            variant.sku = item.sku.strip().upper()
            variant.size = item.size.strip() if item.size else None
            variant.color = item.color.strip() if item.color else None
            variant.selling_price = item.selling_price
            variant.compare_at_price = item.compare_at_price
            variant.cost_price = item.cost_price
            variant.low_stock_threshold = item.low_stock_threshold
            variant.is_active = item.is_active
        else:
            variant = ProductVariant(
                sku=item.sku.strip().upper(),
                size=item.size.strip() if item.size else None,
                color=item.color.strip() if item.color else None,
                selling_price=item.selling_price,
                compare_at_price=item.compare_at_price,
                cost_price=item.cost_price,
                stock_on_hand=item.stock_on_hand,
                stock_reserved=0,
                low_stock_threshold=item.low_stock_threshold,
                is_active=item.is_active,
            )
            product.variants.append(variant)
            db.flush()
            retained.add(variant.id)
            db.add(
                InventoryMovement(
                    variant_id=variant.id,
                    admin_user_id=admin.id,
                    kind="initial",
                    quantity_delta=item.stock_on_hand,
                    stock_after=item.stock_on_hand,
                    note="Stock initial de la variante",
                )
            )
    for variant_id, variant in existing.items():
        if variant_id not in retained:
            variant.is_active = False

    replace_images(product, data)
    audit(db, admin, "product.update", "product", product.id, {"name": product.name})
    db.commit()
    return db.scalar(product_query().where(CatalogProduct.id == product.id))


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_product(
    product_id: int,
    db: DbSession,
    admin: AdminUser = Depends(current_admin),
) -> None:
    product = db.get(CatalogProduct, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Article introuvable")
    product.status = "archived"
    audit(db, admin, "product.archive", "product", product.id, {"name": product.name})
    db.commit()


@router.post("/stock-adjustments", response_model=InventoryMovementRead)
def adjust_stock(
    data: StockAdjustment,
    db: DbSession,
    admin: AdminUser = Depends(current_admin),
) -> InventoryMovement:
    variant = db.scalar(
        select(ProductVariant).where(ProductVariant.id == data.variant_id).with_for_update()
    )
    if variant is None:
        raise HTTPException(status_code=404, detail="Variante introuvable")
    stock_after = variant.stock_on_hand + data.quantity_delta
    if stock_after < variant.stock_reserved:
        raise HTTPException(
            status_code=409,
            detail="Le stock physique ne peut pas devenir inférieur au stock réservé",
        )
    variant.stock_on_hand = stock_after
    movement = InventoryMovement(
        variant_id=variant.id,
        admin_user_id=admin.id,
        kind=data.kind,
        quantity_delta=data.quantity_delta,
        stock_after=stock_after,
        note=data.note.strip(),
    )
    db.add(movement)
    audit(
        db,
        admin,
        "stock.adjust",
        "product_variant",
        variant.id,
        {"delta": data.quantity_delta, "kind": data.kind, "stock_after": stock_after},
    )
    db.commit()
    db.refresh(movement)
    return movement


@router.get("/inventory-movements", response_model=list[InventoryMovementRead])
def inventory_movements(
    db: DbSession,
    _admin: AdminUser = Depends(current_admin),
) -> list[InventoryMovement]:
    return list(
        db.scalars(select(InventoryMovement).order_by(InventoryMovement.created_at.desc()).limit(200))
    )


@router.post("/uploads", response_model=UploadRead, status_code=status.HTTP_201_CREATED)
async def upload_image(
    admin: AdminUser = Depends(current_admin),
    file: UploadFile = File(...),
) -> UploadRead:
    del admin
    settings = get_settings()
    data = await file.read(settings.max_upload_bytes + 1)
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="L’image dépasse la limite de 5 Mo")
    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
            image_format = (image.format or "").upper()
        # On redécode puis réencode l'image : cela retire les métadonnées et
        # évite de conserver d'éventuelles données ajoutées après l'image.
        with Image.open(BytesIO(data)) as image:
            image.seek(0)
            if image.width > 6000 or image.height > 6000 or image.width * image.height > 25_000_000:
                raise HTTPException(status_code=413, detail="Les dimensions de l’image sont trop grandes")
            mode = "RGBA" if image_format in {"PNG", "WEBP"} and "A" in image.getbands() else "RGB"
            normalized = image.convert(mode)
            output = BytesIO()
            normalized.save(output, format=image_format, optimize=True)
            normalized_data = output.getvalue()
    except HTTPException:
        raise
    except (Image.DecompressionBombError, UnidentifiedImageError, OSError):
        raise HTTPException(status_code=415, detail="Le fichier n’est pas une image valide") from None
    extensions = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
    extension = extensions.get(image_format)
    if extension is None:
        raise HTTPException(status_code=415, detail="Formats acceptés : JPG, PNG et WebP")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (upload_dir / filename).write_bytes(normalized_data)
    return UploadRead(url=f"{settings.public_media_base_url.rstrip('/')}/{filename}")
