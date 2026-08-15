import os
import tempfile

_TEST_ENVIRONMENT = {
    "POSTGRES_DB": "test_db",
    "POSTGRES_DB_PORT": "5432",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_password",
    "POSTGRES_HOST": "localhost",
    "PGADMIN_DEFAULT_EMAIL": "test@example.com",
    "PGADMIN_DEFAULT_PASSWORD": "test_password",
    "DATASET_DIR": tempfile.gettempdir(),
    "LOG_DIR": os.path.join(tempfile.gettempdir(), "clothing_store_test_logs"),
    "FRONTEND_CORS_ORIGINS": "http://localhost:5000",
    "ELASTICSEARCH_HOST": "localhost",
    "ELASTICSEARCH_PORT": "9200",
    "ELASTICSEARCH_USER": "elastic",
    "ELASTICSEARCH_PASSWORD": "test_password",
    "ELASTICSEARCH_SCHEME": "http",
    "ELASTICSEARCH_PRODUCTS_INDEX": "test_products",
    "EMAIL_HOST": "localhost",
    "EMAIL_PORT": "1025",
    "EMAIL_HOST_USER": "test_user",
    "EMAIL_HOST_PASSWORD": "test_password",
    "EMAIL_USE_TLS": "False",
    "EMAIL_USE_SSL": "False",
    "JWT_SECRET_KEY_ACCESS": "test_access_secret",
    "JWT_SECRET_KEY_REFRESH": "test_refresh_secret",
    "JWT_SIGNING_ALGORITHM": "HS256",
    "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
    "JWT_REFRESH_TOKEN_EXPIRE_MINUTES": "10080",
    "GOOGLE_CLIENT_ID": "test_google_client_id",
    "GOOGLE_CLIENT_SECRET": "test_google_client_secret",
    "FACEBOOK_CLIENT_ID": "test_facebook_client_id",
    "FACEBOOK_CLIENT_SECRET": "test_facebook_client_secret",
}

for _key, _value in _TEST_ENVIRONMENT.items():
    os.environ[_key] = _value

import pytest

from tests.fakes import FakeConnectionPool


@pytest.fixture
def connection_pool() -> FakeConnectionPool:
    """Connection pool handing out fake connections and recording their use"""
    return FakeConnectionPool()
