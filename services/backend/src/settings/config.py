from pathlib import Path
from urllib.parse import urljoin

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

    # Email settings
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_USE_TLS: str
    EMAIL_USE_SSL: str

    # JWT settings
    JWT_SECRET_KEY_ACCESS: str
    JWT_SECRET_KEY_REFRESH: str
    JWT_SIGNING_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int

    # Google OAuth2 settings
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Facebook OAuth2 settings
    FACEBOOK_CLIENT_ID: str
    FACEBOOK_CLIENT_SECRET: str

    # Token settings
    ACTIVATION_TOKEN_VALID_DAYS: int = 7

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
    def FRONTEND_BASE_URL(self) -> str:
        """Get the first (primary) frontend URL for creating links"""
        origins = self.CORS_ORIGINS
        if origins:
            return origins[0]
        return "http://localhost:5000"

    @property
    def ELASTICSEARCH_URL(self) -> str:
        """Full Elasticsearch URL for client connection"""
        return f"{self.ELASTICSEARCH_SCHEME}://{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    @property
    def ELASTICSEARCH_AUTH(self) -> tuple[str, str]:
        """Elasticsearch authentication tuple (username, password)"""
        return self.ELASTICSEARCH_USER, self.ELASTICSEARCH_PASSWORD

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

    @property
    def EMAIL_CONFIG(self) -> dict:
        """Complete configuration dictionary for email client"""
        use_tls = self.EMAIL_USE_TLS.lower() == "true"
        use_ssl = self.EMAIL_USE_SSL.lower() == "true"

        return {
            "host": self.EMAIL_HOST,
            "port": self.EMAIL_PORT,
            "username": self.EMAIL_HOST_USER,
            "password": self.EMAIL_HOST_PASSWORD,
            "use_tls": use_tls,
            "use_ssl": use_ssl,
            "timeout": 30
        }

    @property
    def JWT_CONFIG(self) -> dict:
        """Complete configuration dictionary for JWT tokens"""
        return {
            "access_secret": self.JWT_SECRET_KEY_ACCESS,
            "refresh_secret": self.JWT_SECRET_KEY_REFRESH,
            "algorithm": self.JWT_SIGNING_ALGORITHM,
            "access_expire_minutes": self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            "refresh_expire_minutes": self.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        }

    @property
    def GOOGLE_OAUTH_CONFIG(self) -> dict:
        """Complete configuration dictionary for Google OAuth2"""
        return {
            "client_id": self.GOOGLE_CLIENT_ID,
            "client_secret": self.GOOGLE_CLIENT_SECRET,
        }

    @property
    def FACEBOOK_OAUTH_CONFIG(self) -> dict:
        """Complete configuration dictionary for Facebook OAuth2"""
        return {
            "client_id": self.FACEBOOK_CLIENT_ID,
            "client_secret": self.FACEBOOK_CLIENT_SECRET,
        }

    def build_frontend_url(self, path: str, **params) -> str:
        """
        Build a frontend URL with given path and query parameters

        Args:
            path: URL path (e.g., '/activate', '/login')
            **params: Query parameters to add to URL

        Returns:
            Complete frontend URL with path and parameters
        """
        base_url = self.FRONTEND_BASE_URL

        if not path.startswith('/'):
            path = '/' + path

        url = urljoin(base_url, path)

        if params:
            from urllib.parse import urlencode
            query_string = urlencode(params)
            url = f"{url}?{query_string}"

        return url


# Global config instance
config = AppConfig()
