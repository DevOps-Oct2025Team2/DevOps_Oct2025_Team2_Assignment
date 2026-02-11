# notify.py
import os
import time
import smtplib
from email.message import EmailMessage

# simple in-memory dedupe to prevent spam
_LAST_SENT = {}

def _env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y")

def route_recipients(event_type: str) -> str:
    if event_type.startswith("security_"):
        return os.getenv("EMAIL_QA", "")
    elif event_type.startswith(("build_", "ops_")):
        return os.getenv("EMAIL_DEV", "")
    else:
        return os.getenv("EMAIL_TEAM", "")

def notify_event(event_type: str, subject: str, body: str, dedupe_key: str = "") -> None:
    """
    Runtime email notification. Safe defaults:
    - Does nothing if ENABLE_RUNTIME_EMAILS is false
    - Rate-limits per event_type to avoid spamming
    """
    if not _env_bool("ENABLE_RUNTIME_EMAILS", "false"):
        return

    rate_limit_s = int(os.getenv("EMAIL_RATE_LIMIT_SECONDS", "60"))

    to_addr = route_recipients(event_type)
    if not to_addr:
        return
    
    key = f"{event_type}:{dedupe_key}" if dedupe_key else event_type

    now = time.time()
    last = _LAST_SENT.get(key, 0)
    if now - last < rate_limit_s:
        return
    _LAST_SENT[key] = now

    send_email_smtp(to_addr, subject, body)

def send_email_smtp(to_addr: str, subject: str, body: str) -> None:
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    from_addr = os.getenv("EMAIL_FROM") or smtp_user
    service = os.getenv("SERVICE_NAME", "file-service")
    env = os.getenv("APP_ENV", "dev")

    # Fail quietly if not configured
    if not (smtp_user and smtp_pass and to_addr):
        return

    msg = EmailMessage()

    # Make subject unique to avoid Gmail threading/throttling
    msg["Subject"] = f"[{env}][{service}] {subject} @ {int(time.time())}"

    # Send to self, notify recipients via BCC
    msg["From"] = from_addr
    msg["To"] = from_addr
    msg["Bcc"] = to_addr

    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=10) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
