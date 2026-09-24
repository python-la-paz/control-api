import logging
import smtplib
from email.message import EmailMessage

from app.core import configuration

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, body: str) -> None:
    if not configuration.APP_SMTP_HOST or not to:
        logger.warning("Email not sent to %s: SMTP not configured or no address", to)
        return
    message = EmailMessage()
    message["From"] = configuration.APP_SMTP_FROM or configuration.APP_SMTP_USER
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(
            configuration.APP_SMTP_HOST,
            configuration.APP_SMTP_PORT,
            timeout=30,
        ) as smtp:
            if configuration.APP_SMTP_STARTTLS:
                smtp.starttls()
            if configuration.APP_SMTP_USER:
                smtp.login(configuration.APP_SMTP_USER, configuration.APP_SMTP_PASSWORD)
            smtp.send_message(message)
    except Exception:
        logger.exception("Failed to send email to %s", to)
