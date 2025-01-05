import logging
from typing import Optional
from ..core.config import settings
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pathlib import Path
import datetime

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.FROM_EMAIL,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_FROM_NAME=settings.APP_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates'
        )
        self.fastmail = FastMail(self.mail_config)
        logger.info("Email Service initialized")

    async def _send_email(
        self,
        email_to: str,
        subject: str,
        body: str,
        template_name: Optional[str] = None,
        template_body: Optional[dict] = None
    ) -> None:
        """Send an email."""
        try:
            message = MessageSchema(
                subject=subject,
                recipients=[email_to],
                body=body,
                template_body=template_body,
                subtype="html"
            )

            if template_name:
                await self.fastmail.send_message(message, template_name=template_name)
            else:
                await self.fastmail.send_message(message)

            logger.info(f"Email sent successfully to {email_to}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    async def send_admin_credentials(self, email: str, name: str, password: str) -> None:
        """Send admin credentials to a newly created admin user."""
        try:
            subject = "Your Admin Account Credentials"
            template_body = {
                "name": name,
                "email": email,
                "password": password,
                "login_url": f"{settings.FRONTEND_URL}/login"
            }

            await self._send_email(
                email_to=email,
                subject=subject,
                body="",  # Body will be provided by template
                template_name="admin_credentials.html",
                template_body=template_body
            )
        except Exception as e:
            logger.error(f"Failed to send admin credentials: {str(e)}")
            raise

    async def send_password_reset_email(self, email: str, name: str, reset_token: str) -> None:
        """Send a password reset email to a user."""
        try:
            logger.info(f"Sending password reset email to {email}")
            subject = "Password Reset Request"
            reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            template_body = {
                "username": name,  # Changed from name to username to match template
                "reset_link": reset_link,
                "logo_url": f"{settings.FRONTEND_URL}/logo.png",  # Add logo URL
                "contact_url": f"{settings.FRONTEND_URL}/contact",
                "privacy_url": f"{settings.FRONTEND_URL}/privacy",
                "terms_url": f"{settings.FRONTEND_URL}/terms",
                "current_year": datetime.datetime.now().year
            }

            await self._send_email(
                email_to=email,
                subject=subject,
                body="",
                template_name="password_reset.html",
                template_body=template_body
            )
            logger.info(f"Password reset email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise

email_service = EmailService() 