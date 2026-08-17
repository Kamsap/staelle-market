from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import AdminUser, Customer
from .security import decode_access_token, decode_admin_access_token


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


ADMIN_COOKIE_NAME = "staelle_admin_session"


def require_trusted_admin_origin(
    origin: Annotated[str | None, Header()] = None,
) -> None:
    """Bloque les requêtes navigateur provenant d'un site non autorisé.

    Les scripts de maintenance sans en-tête Origin restent utilisables.
    """

    if origin and origin.rstrip("/") not in {
        allowed.rstrip("/") for allowed in get_settings().allowed_origins
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origine administrateur non autorisée",
        )


def current_admin(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    admin_cookie: Annotated[str | None, Cookie(alias=ADMIN_COOKIE_NAME)] = None,
) -> AdminUser:
    token = admin_cookie or (credentials.credentials if credentials else None)
    admin_id = decode_admin_access_token(token) if token else None
    admin = db.get(AdminUser, admin_id) if admin_id else None
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Connexion administrateur requise",
        )
    return admin


def require_admin(
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    x_admin_key: Annotated[str | None, Header()] = None,
    admin_cookie: Annotated[str | None, Cookie(alias=ADMIN_COOKIE_NAME)] = None,
) -> None:
    # La clé historique reste utilisable pour les scripts de maintenance.
    if x_admin_key == get_settings().admin_api_key:
        return
    token = admin_cookie or (credentials.credentials if credentials else None)
    admin_id = decode_admin_access_token(token) if token else None
    admin = db.get(AdminUser, admin_id) if admin_id else None
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès administrateur refusé",
        )
