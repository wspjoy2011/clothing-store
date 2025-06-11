"""Password validation functions for accounts app"""

import re


def validate_password_strength(password: str) -> str:
    """
    Validate password strength according to security requirements.

    Args:
        password: Password string to validate

    Returns:
        The validated password string

    Raises:
        ValueError: If password doesn't meet strength requirements
    """
    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    if len(password) > 20:
        raise ValueError("Password must not exceed 20 characters.")

    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter.")

    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit.")

    if not re.search(r'[@$!%*?&#]', password):
        raise ValueError("Password must contain at least one special character: @, $, !, %, *, ?, #, &.")

    return password


def validate_password_format(password: str) -> str:
    """
    Validate basic password format (length and type).

    Args:
        password: Password string to validate

    Returns:
        The validated password string

    Raises:
        ValueError: If password format is invalid
    """
    if not isinstance(password, str):
        raise ValueError("Password must be a string.")

    if not password or password.isspace():
        raise ValueError("Password cannot be empty or contain only whitespace.")

    if len(password) < 1:
        raise ValueError("Password cannot be empty.")

    if len(password) > 20:
        raise ValueError("Password must not exceed 20 characters.")

    return password
