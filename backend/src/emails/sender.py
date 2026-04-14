import os
import smtplib
import socket
import logging
import json
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from dotenv import load_dotenv

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
        logger.warning("Resend fallback is not configured. RESEND_API_KEY set=%s, EMAIL_FROM set=%s", bool(api_key), bool(email_from))
        return 'not_sent:resend_not_configured'

    payload = {
        "from": email_from,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }

    req = urllib.request.Request(
        url="https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=float(os.getenv('EMAIL_HTTP_TIMEOUT', '15'))) as response:
            if 200 <= response.status < 300:
                logger.info("Email sent successfully through Resend API")
                return 'success'

            logger.warning("Resend API returned unexpected status: %s", response.status)
            return 'not_sent:resend_unexpected_status'
    except urllib.error.HTTPError as exc:
        logger.warning("Resend API HTTP error: %s", exc)
        return 'not_sent:resend_http_error'
    except urllib.error.URLError as exc:
        logger.warning("Resend API network error: %s", exc)
        return 'not_sent:resend_network_error'
    except Exception as exc:
        logger.warning("Resend API unknown error: %s", exc)
        return 'not_sent:resend_unknown_error'


def send_email(to_email, subject, body):
    if not all([to_email, subject, body]):
        logger.warning("Missing email parameters")
        return 'not_sent:missing_email_parameters'

    if not _env_bool('EMAIL_NOTIFICATIONS_ENABLED', default=True):
        logger.info("Email notifications disabled by EMAIL_NOTIFICATIONS_ENABLED")
        return 'not_sent:disabled'

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
        return 'not_sent:invalid_smtp_config'

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        logger.warning("Invalid SMTP_PORT value: %s", smtp_port_raw)
        return 'not_sent:invalid_smtp_port'
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
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
        logger.warning("Failed to send email after %s SMTP attempt(s): %s", len(errors), " | ".join(errors))

    if _env_bool('EMAIL_USE_RESEND_FALLBACK', default=True):
        resend_status = _send_with_resend(to_email, subject, body)
        if resend_status == 'success':
            return 'success'

        logger.warning("SMTP unreachable and Resend fallback failed: %s", resend_status)

    return 'not_sent:network_or_smtp_unreachable'