from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    product_name: str = Field(min_length=2, max_length=180)
    displayed_price: int = Field(gt=0)


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
