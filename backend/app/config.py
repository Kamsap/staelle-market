from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DATABASE_URL = "sqlite:///./staelle.db"
DEFAULT_JWT_SECRET = "development-secret-change-me"
DEFAULT_ADMIN_API_KEY = "development-admin-key-change-me"


class Settings(BaseSettings):
    """Configuration chargée depuis l'environnement et les secrets Docker."""

    app_env: str = "development"

    # SQLite reste pratique en développement local. En Docker/production, on peut
    # fournir les morceaux de connexion MariaDB séparément pour éviter de mettre
    # le mot de passe en clair dans DATABASE_URL.
    database_url: str = DEFAULT_DATABASE_URL
    database_host: str | None = None
    database_port: int = 3306
    database_name: str = "staelle_market"
    database_user: str = "staelle"
    database_password: str = ""
    database_password_file: str | None = None

    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_secret_file: str | None = None
    admin_api_key: str = DEFAULT_ADMIN_API_KEY
    admin_api_key_file: str | None = None

    frontend_origins: str = "http://localhost:4200,http://127.0.0.1:4200"
    points_per_xaf: int = 1000
    access_token_minutes: int = 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def model_post_init(self, _context: object) -> None:
        self.database_password = self._read_secret_file(
            self.database_password_file,
            fallback=self.database_password,
        )
        self.jwt_secret = self._read_secret_file(self.jwt_secret_file, fallback=self.jwt_secret)
        self.admin_api_key = self._read_secret_file(
            self.admin_api_key_file,
            fallback=self.admin_api_key,
        )
        self._validate_production_secrets()

    @staticmethod
    def _read_secret_file(path: str | None, fallback: str) -> str:
        if not path:
            return fallback
        return Path(path).read_text(encoding="utf-8").strip()

    def _validate_production_secrets(self) -> None:
        if self.app_env.lower() != "production":
            return

        weak_jwt = self.jwt_secret == DEFAULT_JWT_SECRET or len(self.jwt_secret) < 32
        weak_admin_key = self.admin_api_key == DEFAULT_ADMIN_API_KEY or len(self.admin_api_key) < 32
        if weak_jwt or weak_admin_key:
            raise ValueError(
                "En production, JWT_SECRET et ADMIN_API_KEY doivent être longs, uniques et secrets."
            )

        if self.database_url == DEFAULT_DATABASE_URL and not self.database_host:
            raise ValueError("En production, configure DATABASE_URL ou DATABASE_HOST.")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]

    @property
    def effective_database_url(self) -> str:
        if self.database_host:
            user = quote_plus(self.database_user)
            password = quote_plus(self.database_password)
            host = self.database_host
            port = self.database_port
            database = quote_plus(self.database_name)
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
