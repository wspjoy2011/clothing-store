"""Dependencies for security components"""

from security.passwords import PasswordManager
from security.interfaces import PasswordManagerInterface


def get_password_manager() -> PasswordManagerInterface:
    """
    Get password manager instance

    Returns:
        PasswordManager instance
    """
    return PasswordManager()
