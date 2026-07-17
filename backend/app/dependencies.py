from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import Customer
from .security import decode_access_token


bearer = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db)]


def optional_customer(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> Customer | None:
    if credentials is None:
        return None
    customer_id = decode_access_token(credentials.credentials)
    return db.get(Customer, customer_id) if customer_id else None


def current_customer(customer: Annotated[Customer | None, Depends(optional_customer)]) -> Customer:
    if customer is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Connexion requise")
    return customer


def require_admin(x_admin_key: Annotated[str | None, Header()] = None) -> None:
    if x_admin_key != get_settings().admin_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Clé administrateur invalide")
