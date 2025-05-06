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


# Global config instance
config = AppConfig()
