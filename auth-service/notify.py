# notify.py
import os
import time
import smtplib
from email.message import EmailMessage
from typing import Dict

# In-memory dedupe store to prevent email spam
_LAST_SENT: Dict[str, float] = {}


def _env_bool(name: str, default: str = "false") -> bool:
    """Read boolean env vars safely."""
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y")


def _get_rate_limit(event_type: str) -> int:
    """
    Use stricter rate limit for failed auth events
    """
    if event_type.endswith("_failed"):
        return int(os.getenv("EMAIL_RATE_LIMIT_SECONDS_FAILED", "300"))
    return int(os.getenv("EMAIL_RATE_LIMIT_SECONDS", "60"))


def notify_event(
    event_type: str,
    subject: str,
    body: str,
    dedupe_key: str = ""
) -> None:
    """
    Runtime email notification for auth-service.

    Safe defaults:
    - Disabled unless ENABLE_RUNTIME_EMAILS=true
    - Rate-limited per event_type
    - Deduplicated to prevent spam
    - Fails silently if SMTP is not configured
    """
    if not _env_bool("ENABLE_RUNTIME_EMAILS", "false"):
        return

    rate_limit_s = _get_rate_limit(event_type)
    key = f"{event_type}:{dedupe_key}" if dedupe_key else event_type

    now = time.time()
    last_sent = _LAST_SENT.get(key, 0)

    # Rate-limit / dedupe check
    if now - last_sent < rate_limit_s:
        return

    _LAST_SENT[key] = now
    send_email_smtp(subject, body)


def send_email_smtp(subject: str, body: str) -> None:
    """
    Send email via SMTP (Gmail-friendly).
    Fails quietly so auth flow is never affected.
    """
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    to_addr = os.getenv("RUNTIME_EMAIL_TO")
    from_addr = os.getenv("EMAIL_FROM") or smtp_user

    service = os.getenv("SERVICE_NAME", "auth-service")
    env = os.getenv("APP_ENV", "dev")

    # Do nothing if SMTP is not configured
    if not (smtp_user and smtp_pass and to_addr):
        return

    msg = EmailMessage()
    msg["Subject"] = f"[{env}][{service}] {subject}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    except Exception:
        # Never break auth-service due to email issues
        return
