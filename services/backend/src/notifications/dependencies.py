"""Dependencies for notifications module"""

from pathlib import Path
from functools import lru_cache

from notifications.email.accounts import EmailSender
from notifications.email.interfaces import EmailSenderInterface
from settings.config import config


@lru_cache()
def get_email_sender() -> EmailSenderInterface:
    """
    Create and return a configured EmailSender instance.

    This function is cached to ensure only one instance is created and reused.

    Returns:
        EmailSenderInterface: Configured email sender instance

    Raises:
        EmailTemplateError: If template directory initialization fails
    """
    template_dir = Path(__file__).parent / "email" / "templates"

    email_config = config.EMAIL_CONFIG

    return EmailSender(
        hostname=email_config["host"],
        port=email_config["port"],
        email=email_config["username"],
        password=email_config["password"],
        use_tls=email_config["use_tls"],
        use_ssl=email_config["use_ssl"],
        template_dir=str(template_dir),
        activation_email_template_name="activation_request.html",
        activation_complete_email_template_name="activation_complete.html",
        password_email_template_name="password_reset_request.html",
        password_complete_email_template_name="password_reset_complete.html",
        timeout=email_config.get("timeout", 30),
    )


def get_email_sender_dependency() -> EmailSenderInterface:
    """
    FastAPI dependency function that returns an EmailSender instance.

    This function can be used directly in FastAPI route dependencies.

    Returns:
        EmailSenderInterface: Configured email sender instance
    """
    return get_email_sender()
