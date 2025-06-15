"""Token validation utilities"""

import re
from typing import Optional


def validate_token_format(token: str) -> None:
    """
    Validate activation token format

    Args:
        token: Token string to validate

    Raises:
        ValueError: If token format is invalid
    """
    if not token or not isinstance(token, str):
        raise ValueError("Token must be a non-empty string")

    token = token.strip()

    if len(token) < 10:
        raise ValueError("Token is too short (minimum 10 characters)")

    if len(token) > 256:
        raise ValueError("Token is too long (maximum 256 characters)")

    if not re.match(r'^[a-zA-Z0-9_-]+$', token):
        raise ValueError(
            "Token contains invalid characters. Only letters, numbers, hyphens and underscores are allowed")


def validate_email_token_combination(email: str, token: str) -> None:
    """
    Validate email and token combination

    Args:
        email: Email address
        token: Activation token

    Raises:
        ValueError: If combination is invalid
    """
    if not email or not token:
        raise ValueError("Both email and token are required")

    if not isinstance(email, str) or not isinstance(token, str):
        raise ValueError("Email and token must be strings")

    validate_token_format(token)


def sanitize_token(token: Optional[str]) -> Optional[str]:
    """
    Sanitize token by removing whitespace

    Args:
        token: Token to sanitize

    Returns:
        Sanitized token or None if input is None/empty
    """
    if not token:
        return None

    sanitized = token.strip()
    return sanitized if sanitized else None


def is_valid_token_length(token: str, min_length: int = 10, max_length: int = 256) -> bool:
    """
    Check if token length is within valid range

    Args:
        token: Token to check
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        True if length is valid, False otherwise
    """
    if not token or not isinstance(token, str):
        return False

    length = len(token.strip())
    return min_length <= length <= max_length


def mask_token_for_logging(token: str, visible_chars: int = 6) -> str:
    """
    Mask token for secure logging

    Args:
        token: Token to mask
        visible_chars: Number of characters to show at start and end

    Returns:
        Masked token string
    """
    if not token or len(token) <= visible_chars * 2:
        return "***MASKED***"

    start = token[:visible_chars]
    end = token[-visible_chars:]
    middle_length = len(token) - (visible_chars * 2)

    return f"{start}{'*' * min(middle_length, 10)}{end}"
