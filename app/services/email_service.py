import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.app_name = settings.APP_NAME
        self.frontend_url = settings.FRONTEND_URL

    def _create_smtp_connection(self):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            return server
        except Exception as e:
            logger.error(f"Failed to create SMTP connection: {str(e)}")
            raise

    def _send_email(self, to_email: str, subject: str, html_content: str):
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.app_name} <{self.from_email}>"
            msg['To'] = to_email

            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            with self._create_smtp_connection() as server:
                server.send_message(msg)
                logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise

    def _generate_verification_token(self, email: str, expiration_minutes: int = 60) -> str:
        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        return jwt.encode(
            {
                'email': email,
                'exp': expiration,
                'type': 'email_verification'
            },
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM
        )


    def verify_token(self, token: str, token_type: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            if payload.get('type') != token_type:
                return None
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return None

    def send_verification_email(self, email: str):
        token = self._generate_verification_token(email)
        verification_link = f"{self.frontend_url}/verify-email?token={token}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2>Welcome to {self.app_name}!</h2>
            <p>Please verify your email address by clicking the button below:</p>
            <a href="{verification_link}" style="display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 16px 0;">
                Verify Email
            </a>
            <p>Or copy and paste this link in your browser:</p>
            <p style="color: #4F46E5;">{verification_link}</p>
            <p>This link will expire in 60 minutes.</p>
            <p>If you didn't create an account with us, please ignore this email.</p>
        </div>
        """

        self._send_email(
            to_email=email,
            subject=f"Verify your email - {self.app_name}",
            html_content=html_content
        )

    def send_password_reset_email(self, email: str, reset_link: str):
        """Send password reset email with reset link."""
        try:
            subject = "Reset Your Password"
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Click the button below to set a new password:</p>
                <a href="{reset_link}" style="display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; margin: 16px 0;">
                    Reset Password
                </a>
                <p>Or copy and paste this link in your browser:</p>
                <p style="color: #4F46E5;">{reset_link}</p>
                <p>This link will expire in 15 minutes.</p>
                <p>If you didn't request this, you can safely ignore this email.</p>
                <p>Best regards,<br>{self.app_name} Team</p>
            </div>
            """
            
            self._send_email(
                to_email=email,
                subject=f"Reset your password - {self.app_name}",
                html_content=html_content
            )
            logger.info(f"Password reset email sent to: {email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise

email_service = EmailService() 