from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .catalog_seed import seed_catalog
from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers import admin, auth, catalog, orders


settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Alembic gère les évolutions ; create_all garde le démarrage local très simple.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_catalog(db)
    yield


app = FastAPI(title="Staelle Market API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Ajoute des protections communes, y compris aux erreurs de l'API."""

    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if request.url.path.startswith(("/api/v1/admin", "/api/v1/auth")):
        response.headers["Cache-Control"] = "no-store"
    return response

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/api/v1/media", StaticFiles(directory=settings.upload_dir), name="media")


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(catalog.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
