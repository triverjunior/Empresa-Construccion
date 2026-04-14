import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import traceback

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def send_email(to_email, subject, body):
    if not all([to_email, subject, body]):
        print('Missing email parameters')
        return

    smtp_server = os.getenv('SMTP_SERVER', '').strip()
    smtp_port_raw = os.getenv('SMTP_PORT', '').strip()
    smtp_user = os.getenv('SMTP_USER', '').strip()
    smtp_password = os.getenv('SMTP_PASSWORD', '').strip()
    smtp_use_ssl = _env_bool('SMTP_USE_SSL', default=False)
    smtp_use_tls = _env_bool('SMTP_USE_TLS', default=not smtp_use_ssl)
    smtp_timeout = float(os.getenv('SMTP_TIMEOUT', '15'))

    if not all([smtp_server, smtp_port_raw, smtp_user, smtp_password]):
        print(f"SMTP configuration is incomplete. SERVER: {bool(smtp_server)}, PORT: {bool(smtp_port_raw)}, USER: {bool(smtp_user)}, PASSWORD: {bool(smtp_password)}")
        return

    try:
        smtp_port = int(smtp_port_raw)
    except ValueError:
        print(f"Invalid SMTP_PORT value: {smtp_port_raw}")
        return
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        print(f"Attempting to connect to {smtp_server}:{smtp_port} (SSL={smtp_use_ssl}, TLS={smtp_use_tls})...")
        if smtp_use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=smtp_timeout)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=smtp_timeout)

        with server:
            if smtp_use_tls and not smtp_use_ssl:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully!")
        return 'success'
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        traceback.print_exc()
        return f'Failed to send email: {str(e)}'