import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import traceback

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env')))

def send_email(to_email, subject, body):
    if not all([to_email, subject, body]):
        print('Missing email parameters')
        return

    smtp_server = os.getenv('SMTP_SERVER', '')
    smtp_port = os.getenv('SMTP_PORT', '')
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')

    if not all([smtp_server, smtp_port, smtp_user, smtp_password]):
        print(f"SMTP configuration is incomplete. SERVER: {bool(smtp_server)}, PORT: {bool(smtp_port)}, USER: {bool(smtp_user)}, PASSWORD: {bool(smtp_password)}")
        return
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email

    try:
        print(f"Attempting to connect to {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully!")
        return 'success'
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        traceback.print_exc()
        return f'Failed to send email: {str(e)}'