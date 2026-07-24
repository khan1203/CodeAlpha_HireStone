import logging
import smtplib
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger("notifications")


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send notification email. Falls back to logging if SMTP not configured.

    Swap this for a third-party provider (SendGrid, SES, Postmark) in prod —
    keep the function signature so callers don't change.
    """
    if not settings.smtp_host:
        logger.info("EMAIL STUB -> to=%s subject=%s body=%s", to_email, subject, body)
        return

    msg = EmailMessage()
    msg["From"] = settings.notify_from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


def notify_employer_new_application(employer_email: str, job_title: str, candidate_name: str) -> None:
    send_email(
        employer_email,
        f"New application: {job_title}",
        f"{candidate_name} applied to your job listing '{job_title}'.",
    )


def notify_candidate_status_change(candidate_email: str, job_title: str, new_status: str) -> None:
    send_email(
        candidate_email,
        f"Application update: {job_title}",
        f"Your application status for '{job_title}' changed to '{new_status}'.",
    )
