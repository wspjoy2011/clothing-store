from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for resolving the path to .env
BASE_DIR = Path(__file__).parent.parent.parent


class AppConfig(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # PostgreSQL settings
    POSTGRES_DB: str
    POSTGRES_DB_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str

    # pgAdmin settings
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str

    # Paths
    DATASET_DIR: Path
    LOG_DIR: Path

    # CORS settings
    FRONTEND_CORS_ORIGINS: str

    # Elasticsearch settings
    ELASTICSEARCH_HOST: str
    ELASTICSEARCH_PORT: int
    ELASTICSEARCH_USER: str
    ELASTICSEARCH_PASSWORD: str
    ELASTICSEARCH_SCHEME: str
    ELASTICSEARCH_PRODUCTS_INDEX: str

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8"
    )

    @property
    def STYLES_CSV(self) -> Path:
        """Full path to styles_clean.csv"""
        return self.DATASET_DIR / "styles_clean.csv"

    @property
    def IMAGES_CSV(self) -> Path:
        """Full path to images.csv"""
        return self.DATASET_DIR / "images.csv"

    @property
    def CORS_ORIGINS(self) -> list[str]:
        """Parse the comma-separated list of allowed origins for CORS"""
        return [origin.strip() for origin in self.FRONTEND_CORS_ORIGINS.split(",")]

    @property
    def ELASTICSEARCH_URL(self) -> str:
        """Full Elasticsearch URL for client connection"""
        return f"{self.ELASTICSEARCH_SCHEME}://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    @property
    def ELASTICSEARCH_AUTH(self) -> tuple[str, str]:
        """Elasticsearch authentication tuple (username, password)"""
        return (self.ELASTICSEARCH_USER, self.ELASTICSEARCH_PASSWORD)

    @property
    def ELASTICSEARCH_CLIENT_CONFIG(self) -> dict:
        """Complete configuration dictionary for Elasticsearch client"""
        return {
            "hosts": [self.ELASTICSEARCH_URL],
            "http_auth": self.ELASTICSEARCH_AUTH,
            "verify_certs": False,
            "ssl_show_warn": False,
            "request_timeout": 30,
            "retry_on_timeout": True,
            "max_retries": 3
        }


# Global config instance
config = AppConfig()
