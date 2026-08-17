"""Dependencies for security components"""

from security.interfaces import JWTManagerInterface, PasswordManagerInterface
from security.jwt_token import JWTManager
from security.passwords import PasswordManager
from settings.config import config


def get_password_manager() -> PasswordManagerInterface:
    """
    Get password manager instance

    Returns:
        PasswordManager instance
    """
    return PasswordManager()


def get_jwt_manager() -> JWTManagerInterface:
    """
    Get JWT manager instance

    Returns:
        JWTManager instance configured with settings
    """
    jwt_config = config.JWT_CONFIG
    return JWTManager(
        access_secret=jwt_config["access_secret"],
        refresh_secret=jwt_config["refresh_secret"],
        algorithm=jwt_config["algorithm"],
        access_expire_minutes=jwt_config["access_expire_minutes"],
        refresh_expire_minutes=jwt_config["refresh_expire_minutes"]
    )
