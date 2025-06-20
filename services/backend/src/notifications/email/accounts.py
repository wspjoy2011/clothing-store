from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from notifications.exceptions.email import (
    BaseEmailError,
    EmailConnectionError,
    EmailAuthenticationError,
    EmailSendError,
    EmailTemplateError
)
from notifications.email.interfaces import EmailSenderInterface
from settings.logging_config import get_logger


class EmailSender(EmailSenderInterface):

    def __init__(
            self,
            hostname: str,
            port: int,
            email: str,
            password: str,
            use_tls: bool,
            use_ssl: bool,
            template_dir: str,
            activation_email_template_name: str,
            resend_activation_email_template_name: str,
            activation_complete_email_template_name: str,
            password_email_template_name: str,
            password_complete_email_template_name: str,
            timeout: int = 30,
    ):
        self._hostname = hostname
        self._port = port
        self._email = email
        self._password = password
        self._use_tls = use_tls
        self._use_ssl = use_ssl
        self._timeout = timeout
        self._activation_email_template_name = activation_email_template_name
        self._resend_activation_email_template_name = resend_activation_email_template_name
        self._activation_complete_email_template_name = activation_complete_email_template_name
        self._password_email_template_name = password_email_template_name
        self._password_complete_email_template_name = password_complete_email_template_name

        try:
            self._env = Environment(loader=FileSystemLoader(template_dir))
        except Exception as e:
            raise EmailTemplateError(f"Failed to initialize template environment: {e}", e)

        self._logger = get_logger(__name__, "email_notifications")

        self._logger.info(f"EmailSender initialized for host {hostname}:{port}")

    async def _send_email(self, recipient: str, subject: str, html_content: str) -> None:
        """
        Asynchronously send an email with the given subject and HTML content.

        Args:
            recipient (str): The recipient's email address.
            subject (str): The subject of the email.
            html_content (str): The HTML content of the email.

        Raises:
            EmailConnectionError: If connection to SMTP server fails.
            EmailAuthenticationError: If authentication fails.
            EmailSendError: If sending the email fails.
        """
        self._logger.info(f"Attempting to send email to {recipient} with subject: {subject}")

        message = MIMEMultipart()
        message["From"] = self._email
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        smtp = None
        try:
            if self._use_ssl:
                smtp = aiosmtplib.SMTP(
                    hostname=self._hostname,
                    port=self._port,
                    use_tls=True,
                    timeout=self._timeout
                )
            else:
                smtp = aiosmtplib.SMTP(
                    hostname=self._hostname,
                    port=self._port,
                    start_tls=self._use_tls,
                    timeout=self._timeout
                )

            await smtp.connect()
            self._logger.debug(f"Connected to SMTP server {self._hostname}:{self._port}")

            if self._use_tls and not self._use_ssl:
                await smtp.starttls()
                self._logger.debug("TLS connection established")

            if self._email and self._password:
                await smtp.login(self._email, self._password)
                self._logger.debug("SMTP authentication successful")

            await smtp.sendmail(self._email, [recipient], message.as_string())
            self._logger.info(f"Email successfully sent to {recipient}")

        except aiosmtplib.SMTPConnectError as e:
            error_msg = f"Failed to connect to SMTP server {self._hostname}:{self._port}"
            self._logger.error(f"{error_msg}: {e}")
            raise EmailConnectionError(error_msg, e)

        except aiosmtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed for {self._email}"
            self._logger.error(f"{error_msg}: {e}")
            raise EmailAuthenticationError(error_msg, e)

        except aiosmtplib.SMTPException as e:
            error_msg = f"Failed to send email to {recipient}"
            self._logger.error(f"{error_msg}: {e}")
            raise EmailSendError(error_msg, e)

        except Exception as e:
            error_msg = f"Unexpected error while sending email to {recipient}"
            self._logger.error(f"{error_msg}: {e}")
            raise BaseEmailError(error_msg, e)

        finally:
            if smtp:
                try:
                    await smtp.quit()
                    self._logger.debug("SMTP connection closed")
                except Exception as e:
                    self._logger.warning(f"Error closing SMTP connection: {e}")

    def _render_template(self, template_name: str, **kwargs) -> str:
        """
        Render email template with given context.

        Args:
            template_name (str): Name of the template file.
            **kwargs: Template context variables.

        Returns:
            str: Rendered HTML content.

        Raises:
            EmailTemplateError: If template rendering fails.
        """
        try:
            template = self._env.get_template(template_name)
            return template.render(**kwargs)
        except TemplateNotFound as e:
            error_msg = f"Email template '{template_name}' not found"
            self._logger.error(error_msg)
            raise EmailTemplateError(error_msg, e)
        except Exception as e:
            error_msg = f"Failed to render template '{template_name}'"
            self._logger.error(f"{error_msg}: {e}")
            raise EmailTemplateError(error_msg, e)

    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """
        Send an account activation email asynchronously.

        Args:
            email (str): The recipient's email address.
            activation_link (str): The activation link to be included in the email.
        """
        self._logger.info(f"Preparing activation email for {email}")

        try:
            html_content = self._render_template(
                self._activation_email_template_name,
                email=email,
                activation_link=activation_link
            )
            subject = "Account Activation"
            await self._send_email(email, subject, html_content)
        except (EmailTemplateError, BaseEmailError):
            raise
        except Exception as e:
            error_msg = f"Unexpected error sending activation email to {email}"
            self._logger.error(f"{error_msg}: {e}")
            raise BaseEmailError(error_msg, e)

    async def send_resend_activation_email(self, email: str, activation_link: str) -> None:
        """
        Send a resend activation email asynchronously.

        Args:
            email (str): The recipient's email address.
            activation_link (str): The activation link to be included in the email.
        """
        self._logger.info(f"Preparing resend activation email for {email}")

        try:
            html_content = self._render_template(
                self._resend_activation_email_template_name,
                email=email,
                activation_link=activation_link
            )
            subject = "New Activation Link - Account Activation"
            await self._send_email(email, subject, html_content)
        except (EmailTemplateError, BaseEmailError):
            raise
        except Exception as e:
            error_msg = f"Unexpected error sending resend activation email to {email}"
            self._logger.error(f"{error_msg}: {e}")
            raise BaseEmailError(error_msg, e)

    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """
        Send an account activation completion email asynchronously.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to be included in the email.
        """
        self._logger.info(f"Preparing activation complete email for {email}")

        try:
            html_content = self._render_template(
                self._activation_complete_email_template_name,
                email=email,
                login_link=login_link
            )
            subject = "Account Activated Successfully"
            await self._send_email(email, subject, html_content)
        except (EmailTemplateError, BaseEmailError):
            raise
        except Exception as e:
            error_msg = f"Unexpected error sending activation complete email to {email}"
            self._logger.error(f"{error_msg}: {e}")
            raise BaseEmailError(error_msg, e)

    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """
        Send a password reset request email asynchronously.

        Args:
            email (str): The recipient's email address.
            reset_link (str): The reset link to be included in the email.
        """
        self._logger.info(f"Preparing password reset email for {email}")

        try:
            html_content = self._render_template(
                self._password_email_template_name,
                email=email,
                reset_link=reset_link
            )
            subject = "Password Reset Request"
            await self._send_email(email, subject, html_content)
        except (EmailTemplateError, BaseEmailError):
            raise
        except Exception as e:
            error_msg = f"Unexpected error sending password reset email to {email}"
            self._logger.error(f"{error_msg}: {e}")
            raise BaseEmailError(error_msg, e)

    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """
        Send a password reset completion email asynchronously.

        Args:
            email (str): The recipient's email address.
            login_link (str): The login link to be included in the email.
        """
        self._logger.info(f"Preparing password reset complete email for {email}")

        try:
            html_content = self._render_template(
                self._password_complete_email_template_name,
                email=email,
                login_link=login_link
            )
            subject = "Your Password Has Been Successfully Reset"
            await self._send_email(email, subject, html_content)
        except (EmailTemplateError, BaseEmailError):
            raise
        except Exception as e:
            error_msg = f"Unexpected error sending password reset complete email to {email}"
            self._logger.error(f"{error_msg}: {e}")
            raise BaseEmailError(error_msg, e)
