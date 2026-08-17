from datetime import datetime

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class CustomerRegister(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=30)
    password: str = Field(min_length=8, max_length=128)


class CustomerLogin(BaseModel):
    email: EmailStr
    password: str


class CustomerRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    points: int

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    customer: CustomerRead


class OrderCreate(BaseModel):
    reference: str = Field(pattern=r"^SM-[A-Z0-9-]{6,32}$")
    product_id: int = Field(gt=0)
    variant_id: int | None = Field(default=None, gt=0)


class OrderConfirm(BaseModel):
    amount_paid: int = Field(gt=0)


class OrderRead(BaseModel):
    id: int
    reference: str
    customer_id: int | None
    product_id: int
    product_name: str
    displayed_price: int
    amount_paid: int | None
    status: str
    points_earned: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Administration ---------------------------------------------------------


class AdminBootstrap(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class AdminLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AdminRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


class ProductImageWrite(BaseModel):
    path: str = Field(min_length=1, max_length=500)
    alt_text: str = Field(default="", max_length=180)
    position: int = Field(default=0, ge=0, le=20)


class ProductImageRead(ProductImageWrite):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductVariantWrite(BaseModel):
    id: int | None = Field(default=None, gt=0)
    sku: str = Field(min_length=2, max_length=80)
    size: str | None = Field(default=None, max_length=60)
    color: str | None = Field(default=None, max_length=120)
    selling_price: int = Field(gt=0)
    compare_at_price: int | None = Field(default=None, gt=0)
    cost_price: int | None = Field(default=None, ge=0)
    stock_on_hand: int = Field(default=0, ge=0)
    stock_reserved: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=2, ge=0, le=100000)
    is_active: bool = True

    @model_validator(mode="after")
    def validate_stock(self) -> "ProductVariantWrite":
        if self.stock_reserved > self.stock_on_hand:
            raise ValueError("Le stock réservé ne peut pas dépasser le stock physique")
        return self


class ProductVariantRead(ProductVariantWrite):
    id: int
    available_stock: int

    model_config = ConfigDict(from_attributes=True)


class ProductWrite(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    slug: str = Field(min_length=2, max_length=190, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    brand: str = Field(min_length=1, max_length=60)
    category: str = Field(min_length=1, max_length=60)
    description: str = Field(min_length=2, max_length=5000)
    status: Literal["draft", "active", "archived"] = "active"
    featured: bool = False
    variants: list[ProductVariantWrite] = Field(min_length=1, max_length=50)
    images: list[ProductImageWrite] = Field(default_factory=list, max_length=10)


class ProductAdminRead(ProductWrite):
    id: int
    variants: list[ProductVariantRead]
    images: list[ProductImageRead]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductPublicRead(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    price: int
    stock: int
    size: str | None
    color: str | None
    description: str
    image: str
    images: list[str]
    featured: bool


class StockAdjustment(BaseModel):
    variant_id: int = Field(gt=0)
    quantity_delta: int = Field(ge=-100000, le=100000)
    kind: Literal["receipt", "sale", "return", "correction", "damaged"]
    note: str = Field(min_length=2, max_length=255)

    @model_validator(mode="after")
    def validate_delta(self) -> "StockAdjustment":
        if self.quantity_delta == 0:
            raise ValueError("La variation de stock ne peut pas être nulle")
        return self


class InventoryMovementRead(BaseModel):
    id: int
    variant_id: int
    admin_user_id: int | None
    kind: str
    quantity_delta: int
    stock_after: int
    note: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminDashboardRead(BaseModel):
    active_products: int
    total_available_stock: int
    low_stock_variants: int
    pending_orders: int
    confirmed_revenue: int


class UploadRead(BaseModel):
    url: str
