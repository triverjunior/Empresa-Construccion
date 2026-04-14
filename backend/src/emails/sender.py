import os
import smtplib
import socket
import logging
import re
from email.mime.text import MIMEText
from dotenv import load_dotenv
import resend

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _build_smtp_candidates(smtp_port: int, smtp_use_ssl: bool, smtp_use_tls: bool):
    candidates = [(smtp_port, smtp_use_ssl, smtp_use_tls)]

    # Common provider fallback ports. Keeps original settings first.
    if smtp_port != 465:
        candidates.append((465, True, False))
    if smtp_port != 587:
        candidates.append((587, False, True))

    unique_candidates = []
    for candidate in candidates:
        if candidate not in unique_candidates:
            unique_candidates.append(candidate)
    return unique_candidates


def _send_with_resend(to_email: str, subject: str, body: str) -> str:
    api_key = os.getenv('RESEND_API_KEY', '').strip()
    email_from = os.getenv('EMAIL_FROM', '').strip()

    if not api_key or not email_from:
        logger.warning("Resend is not configured. RESEND_API_KEY set=%s, EMAIL_FROM set=%s", bool(api_key), bool(email_from))
        return 'not_sent:resend_not_configured'

    resend.api_key = api_key

    payload = {
        "from": email_from,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }

    try:
        response = resend.Emails.send(payload)
        response_id = response.get("id") if isinstance(response, dict) else None
        logger.info("Email sent successfully through Resend SDK (id=%s)", response_id)
        return 'success'
    except Exception as exc:
        raw_error = str(exc)
        status_match = re.search(r"\b(?:status|status_code)\s*[:=]\s*(\d{3})\b", raw_error, flags=re.IGNORECASE)
        code_match = re.search(r"\berror\s*code\s*[:=]\s*(\d+)\b", raw_error, flags=re.IGNORECASE)
        status_code = int(status_match.group(1)) if status_match else None
        error_code = code_match.group(1) if code_match else None

        logger.warning(
            "Resend SDK error: status=%s error_code=%s details=%s",
            status_code,
            error_code,
            raw_error,
        )

        if status_code == 401:
            return 'not_sent:resend_unauthorized'
        if status_code == 422:
            return 'not_sent:resend_unprocessable'
        if status_code == 403 and error_code == '1010':
            logger.warning(
                "Resend rejected the sender or recipient (403/1010). Check EMAIL_FROM domain verification and recipient restrictions in Resend."
            )
            return 'not_sent:resend_forbidden_1010'
        if status_code == 403:
            return 'not_sent:resend_forbidden'
        return 'not_sent:resend_unknown_error'


def send_email(to_email, subject, body):
    if not all([to_email, subject, body]):
        logger.warning("Missing email parameters")
        return 'not_sent:missing_email_parameters'

    if not _env_bool('EMAIL_NOTIFICATIONS_ENABLED', default=True):
        logger.info("Email notifications disabled by EMAIL_NOTIFICATIONS_ENABLED")
        return 'not_sent:disabled'

    resend_status = _send_with_resend(to_email, subject, body)
    if resend_status == 'success':
        return 'success'

    logger.warning("Primary Resend send failed: %s", resend_status)

    if not _env_bool('EMAIL_USE_SMTP_FALLBACK', default=False):
        return resend_status

    smtp_server = os.getenv('SMTP_SERVER', '').strip()
    smtp_port_raw = os.getenv('SMTP_PORT', '').strip()
    smtp_user = os.getenv('SMTP_USER', '').strip()
    smtp_password = os.getenv('SMTP_PASSWORD', '').strip()
    smtp_use_ssl = _env_bool('SMTP_USE_SSL', default=False)
    smtp_use_tls = _env_bool('SMTP_USE_TLS', default=not smtp_use_ssl)
    smtp_timeout = float(os.getenv('SMTP_TIMEOUT', '15'))

    if not all([smtp_server, smtp_port_raw, smtp_user, smtp_password]):
        logger.warning(
            "SMTP configuration is incomplete. SERVER: %s, PORT: %s, USER: %s, PASSWORD: %s",
            bool(smtp_server),
            bool(smtp_port_raw),
            bool(smtp_user),
            bool(smtp_password),
        )
        return resend_status

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        logger.warning("Invalid SMTP_PORT value: %s", smtp_port_raw)
        return resend_status
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_FROM', '').strip() or smtp_user
    msg['To'] = to_email

    errors = []
    allow_fallback = _env_bool('SMTP_ALLOW_FALLBACK', default=True)
    candidates = _build_smtp_candidates(smtp_port, smtp_use_ssl, smtp_use_tls) if allow_fallback else [(smtp_port, smtp_use_ssl, smtp_use_tls)]

    for port, use_ssl, use_tls in candidates:
        try:
            logger.info("Attempting SMTP connection to %s:%s (SSL=%s, TLS=%s)", smtp_server, port, use_ssl, use_tls)

            if use_ssl:
                server = smtplib.SMTP_SSL(smtp_server, port, timeout=smtp_timeout)
            else:
                server = smtplib.SMTP(smtp_server, port, timeout=smtp_timeout)

            with server:
                if use_tls and not use_ssl:
                    server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

            logger.info("Email sent successfully")
            return 'success'
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed for user %s", smtp_user)
            return 'not_sent:auth_failed'
        except (OSError, socket.timeout, smtplib.SMTPConnectError) as exc:
            errors.append(f"{smtp_server}:{port} -> {exc}")
            continue
        except Exception as exc:
            errors.append(f"{smtp_server}:{port} -> {exc}")
            continue

    if errors:
        logger.warning("Resend failed and SMTP fallback also failed after %s attempt(s): %s", len(errors), " | ".join(errors))

    return resend_status