from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[str] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(255))
    points: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
    loyalty_entries: Mapped[list["LoyaltyEntry"]] = relationship(back_populates="customer")


class AdminUser(Base):
    """Compte séparé des clients pour protéger l'espace d'administration."""

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="manager")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    inventory_movements: Mapped[list["InventoryMovement"]] = relationship(
        back_populates="admin"
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="admin")


class CatalogProduct(Base):
    """Article commercial. Les tailles, prix et stocks vivent dans ses variantes."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180))
    slug: Mapped[str] = mapped_column(String(190), unique=True, index=True)
    brand: Mapped[str] = mapped_column(String(60))
    category: Mapped[str] = mapped_column(String(60))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductVariant.id",
    )
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.position",
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    sku: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    size: Mapped[str | None] = mapped_column(String(60), nullable=True)
    color: Mapped[str | None] = mapped_column(String(120), nullable=True)
    selling_price: Mapped[int] = mapped_column(Integer)
    compare_at_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cost_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stock_on_hand: Mapped[int] = mapped_column(Integer, default=0)
    stock_reserved: Mapped[int] = mapped_column(Integer, default=0)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    product: Mapped[CatalogProduct] = relationship(back_populates="variants")
    movements: Mapped[list["InventoryMovement"]] = relationship(back_populates="variant")

    @property
    def available_stock(self) -> int:
        return max(0, self.stock_on_hand - self.stock_reserved)


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    path: Mapped[str] = mapped_column(String(500))
    alt_text: Mapped[str] = mapped_column(String(180), default="")
    position: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[CatalogProduct] = relationship(back_populates="images")


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    variant_id: Mapped[int] = mapped_column(ForeignKey("product_variants.id"), index=True)
    admin_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_users.id"), nullable=True
    )
    kind: Mapped[str] = mapped_column(String(30))
    quantity_delta: Mapped[int] = mapped_column(Integer)
    stock_after: Mapped[int] = mapped_column(Integer)
    note: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    variant: Mapped[ProductVariant] = relationship(back_populates="movements")
    admin: Mapped[AdminUser | None] = relationship(back_populates="inventory_movements")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    admin_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_users.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    admin: Mapped[AdminUser | None] = relationship(back_populates="audit_logs")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    product_id: Mapped[int] = mapped_column(Integer)
    variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_variants.id"), nullable=True
    )
    product_name: Mapped[str] = mapped_column(String(180))
    displayed_price: Mapped[int] = mapped_column(Integer)
    amount_paid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    customer: Mapped[Customer | None] = relationship(back_populates="orders")
    loyalty_entry: Mapped["LoyaltyEntry | None"] = relationship(back_populates="order")


class LoyaltyEntry(Base):
    __tablename__ = "loyalty_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), unique=True)
    points: Mapped[int] = mapped_column(Integer)
    reason: Mapped[str] = mapped_column(String(180))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    customer: Mapped[Customer] = relationship(back_populates="loyalty_entries")
    order: Mapped[Order] = relationship(back_populates="loyalty_entry")
