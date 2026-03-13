import smtplib
from email.message import EmailMessage


def send_error_mail(smtpsettings, current_backup, message):
    LOGINUSER = smtpsettings["Login"]
    SENDER = smtpsettings["Sender"]
    SMTP_SERVER = smtpsettings["SMTP_Server"]
    SMTP_PORT = smtpsettings["Port"]
    PASSWORD = smtpsettings["Password"]
    RECIPIENT = smtpsettings["Recipent"]

    msg = EmailMessage()
    msg.set_content(message)
    msg["Subject"] = f"Error - Borgbackup for Backup '{current_backup}'"
    msg["From"] = SENDER
    msg["To"] = RECIPIENT

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(LOGINUSER, PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Error: {e}")
