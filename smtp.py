import smtplib
import email
from datetime import datetime
from zoneinfo import ZoneInfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(smtpsettings, message):
    LOGINUSER = smtpsettings["Login"]
    SENDER = smtpsettings["Sender"]
    SMTP_SERVER = smtpsettings["SMTP_Server"]
    SMTP_PORT = smtpsettings["Port"]
    PASSWORD = smtpsettings["Password"]
    RECIPIENT = smtpsettings["Recipient"]
    today = datetime.now().strftime("%Y-%m-%d")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[BorgBackup] Backup report: tmp - {today}"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg["Date"] = email.utils.format_datetime(
        datetime.now(ZoneInfo(smtpsettings["DateHeaderTimezone"]))
    )

    msg.attach(MIMEText(message, "html"))

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(LOGINUSER, PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error: {e}")
