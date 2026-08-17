"""Token helpers used when writing to the log."""


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
