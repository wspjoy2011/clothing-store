"""Factory for creating email sender instances"""

from pathlib import Path
from typing import Optional

from notifications.email.accounts import EmailSender
from notifications.email.interfaces import EmailSenderInterface
from settings.config import config


class EmailSenderFactory:
    """Factory for creating configured EmailSender instances"""

    @staticmethod
    def create_email_sender(
            template_dir: Optional[str] = None,
            activation_template: str = "activation_request.html",
            activation_complete_template: str = "activation_complete.html",
            password_reset_template: str = "password_reset_request.html",
            password_reset_complete_template: str = "password_reset_complete.html",
    ) -> EmailSenderInterface:
        """
        Create a configured EmailSender instance.

        Args:
            template_dir: Path to email templates directory.
                         If None, uses default templates directory.
            activation_template: Name of activation email template
            activation_complete_template: Name of activation complete email template
            password_reset_template: Name of password reset email template
            password_reset_complete_template: Name of password reset complete email template

        Returns:
            EmailSenderInterface: Configured email sender instance
        """
        if template_dir is None:
            template_dir = str(Path(__file__).parent / "email" / "templates")

        email_config = config.EMAIL_CONFIG

        return EmailSender(
            hostname=email_config["host"],
            port=email_config["port"],
            email=email_config["username"],
            password=email_config["password"],
            use_tls=email_config["use_tls"],
            use_ssl=email_config["use_ssl"],
            template_dir=template_dir,
            activation_email_template_name=activation_template,
            activation_complete_email_template_name=activation_complete_template,
            password_email_template_name=password_reset_template,
            password_complete_email_template_name=password_reset_complete_template,
            timeout=email_config.get("timeout", 30),
        )

    @staticmethod
    def create_for_development() -> EmailSenderInterface:
        """
        Create EmailSender configured for development (MailHog).

        Returns:
            EmailSenderInterface: EmailSender configured for development
        """
        return EmailSenderFactory.create_email_sender()

    @staticmethod
    def create_for_production(
            smtp_host: str,
            smtp_port: int,
            username: str,
            password: str,
            use_tls: bool = True,
            use_ssl: bool = False,
    ) -> EmailSenderInterface:
        """
        Create EmailSender configured for production environment.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            use_tls: Whether to use TLS encryption
            use_ssl: Whether to use SSL encryption

        Returns:
            EmailSenderInterface: EmailSender configured for production
        """
        template_dir = str(Path(__file__).parent / "email" / "templates")

        return EmailSender(
            hostname=smtp_host,
            port=smtp_port,
            email=username,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            template_dir=template_dir,
            activation_email_template_name="activation_request.html",
            activation_complete_email_template_name="activation_complete.html",
            password_email_template_name="password_reset_request.html",
            password_complete_email_template_name="password_reset_complete.html",
            timeout=30,
        )
