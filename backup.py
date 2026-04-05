import json
import os
import sys
import datetime
import traceback
from smtp import *
from Logging import *
from functions import *

Path_config = f"{os.path.dirname(os.path.abspath(__file__))}/config/config.json"

i = 0
for arg in sys.argv:
    if arg.startswith("--config_file="):
        Path_config = f"{sys.argv[i].replace("--config_file=", "")}"
    i = i + 1
with open(Path_config, "r") as file:
    json_data = json.load(file)

Logfolder = json_data["General"]["Logfolder"]
Timestamp = json_data["General"]["Timestamp"]
LogLevel = json_data["General"]["LogLevel"]

for backup in json_data["backup"]:
    Mail_succ = False
    Mail_warn = False
    Mail_err = False
    MailMessage = ""

    try:
        Name = backup["Name"]
        active = backup["active"]
        Initialized = backup["Repo_Initialized"]
        RemoteRepo = backup["RemoteRepo"].replace("{$Name}", Name)
        ArchiveName = backup["ArchiveName"].replace("$Timestamp", Timestamp)
        SourcePath = backup["SourcePath"]
        Logging_Folder_Filename = f"{Logfolder}{Name}/{datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log"

        MailMessage += LOG_INFO(
            f"Current Backup: {Name}", Logging_Folder_Filename, LogLevel
        )

        if active:
            os.environ["BORG_PASSPHRASE"] = backup["EncryptionPwd"]

            if Initialized:
                MailMessage += LOG_INFO(
                    "The repo is initialized.", Logging_Folder_Filename, LogLevel
                )
                returnfunc = borg_create(json_data, backup, Logging_Folder_Filename)
            elif Initialized == False:
                MailMessage += LOG_INFO(
                    "The repo isn't currently initialized.",
                    Logging_Folder_Filename,
                    LogLevel,
                )
                returnfunc = borg_init(json_data, backup, Logging_Folder_Filename)
        else:
            Mail_warn = True
            MailMessage += LOG_WARNING(
                f"Backup '{Name}' is not active.", Logging_Folder_Filename, LogLevel
            )
        MailMessage += returnfunc[1]
    except Exception as e:
        Mail_err = True
        MailMessage += LOG_FATAL(
            f"There were a unhandled Error while Backing up '{Name}':",
            Logging_Folder_Filename,
            LogLevel,
        )
        MailMessage += LOG_FATAL(
            f"\t{e.args[0]}",
            Logging_Folder_Filename,
            LogLevel,
        )
        returnfunc = [3]
    finally:
        MailMessage += LOG_INFO(
            f"Backup '{Name}' done.", Logging_Folder_Filename, LogLevel
        )
        LOG_INFO("--------------------------------", Logging_Folder_Filename, LogLevel)
        os.environ["BORG_PASSPHRASE"] = (
            "We are the Borg. Lower your shields and surrender your ships. We will add your biological and technological distinctiveness to our own. Your culture will adapt to service us. Resistance is futile."
        )

        SendMail_Success = json_data["SMTP"]["SendMailOn"]["Success"]
        SendMail_Warning = json_data["SMTP"]["SendMailOn"]["Warning"]
        SendMail_Error = json_data["SMTP"]["SendMailOn"]["Error"]
        SendMail_Fatal = json_data["SMTP"]["SendMailOn"]["Fatal"]

        if True in (SendMail_Success, SendMail_Warning, SendMail_Error, SendMail_Fatal):
            returncode_func = returnfunc[0]
            MailMessage = MailMessage.replace("\n\n", "\n")

            if returncode_func == 0:
                Mail_status = "Successful"
            elif returncode_func == 1:
                Mail_status = "Warning"
            elif returncode_func == 2:
                Mail_status = "Error"
            elif returncode_func == 3:
                Mail_status = "Fatal"

            send_mail(
                json_data["SMTP"],
                Name,
                MailMessage,
                Mail_status,
            )
