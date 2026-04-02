import smtplib
import email
from datetime import datetime
from zoneinfo import ZoneInfo


def send_mail(smtpsettings, current_backup, message, status):
    LOGINUSER = smtpsettings["Login"]
    SENDER = smtpsettings["Sender"]
    SMTP_SERVER = smtpsettings["SMTP_Server"]
    SMTP_PORT = smtpsettings["Port"]
    PASSWORD = smtpsettings["Password"]
    RECIPIENT = smtpsettings["Recipent"]

    msg = email.message.EmailMessage()
    msg.set_content(message)
    msg["Subject"] = f"{status} - Borgbackup for Backup '{current_backup}'"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT
    msg["Date"] = email.utils.format_datetime(
        datetime.now(ZoneInfo(smtpsettings["DateHeaderTimezone"]))
    )

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(LOGINUSER, PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error: {e}")
