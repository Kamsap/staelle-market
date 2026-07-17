from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from ..dependencies import DbSession, current_customer
from ..models import Customer
from ..schemas import CustomerLogin, CustomerRead, CustomerRegister, TokenResponse
from ..security import create_access_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])


def token_response(customer: Customer) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(customer.id),
        customer=CustomerRead.model_validate(customer),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: CustomerRegister, db: DbSession) -> TokenResponse:
    email = data.email.lower()
    if db.scalar(select(Customer).where(Customer.email == email)):
        raise HTTPException(status_code=409, detail="Un compte utilise déjà cet e-mail")

    customer = Customer(
        full_name=data.full_name.strip(),
        email=email,
        phone=data.phone.strip(),
        password_hash=hash_password(data.password),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return token_response(customer)


@router.post("/login", response_model=TokenResponse)
def login(data: CustomerLogin, db: DbSession) -> TokenResponse:
    customer = db.scalar(select(Customer).where(Customer.email == data.email.lower()))
    if customer is None or not verify_password(data.password, customer.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou mot de passe incorrect")
    return token_response(customer)


@router.get("/me", response_model=CustomerRead)
def me(customer: Annotated[Customer, Depends(current_customer)]) -> Customer:
    return customer
