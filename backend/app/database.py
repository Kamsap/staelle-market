from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
is_sqlite = settings.effective_database_url.startswith("sqlite")
engine = create_engine(
    settings.effective_database_url,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


if is_sqlite:
    # SQLite désactive les clés étrangères par défaut : on les active à chaque connexion.
    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
