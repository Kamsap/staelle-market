from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import Base, engine
from .routers import auth, orders


settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Suffisant pour le MVP. Alembic prendra ensuite en charge les migrations de production.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Staelle Market API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
