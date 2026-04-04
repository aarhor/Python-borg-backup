import json
import subprocess
import os
import sys
import datetime
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

    try:
        Name = backup["Name"]
        active = backup["active"]
        Initialized = backup["Repo_Initialized"]
        RemoteRepo = backup["RemoteRepo"].replace("{$Name}", Name)
        ArchiveName = backup["ArchiveName"].replace("$Timestamp", Timestamp)
        SourcePath = backup["SourcePath"]
        Logging_Folder_Filename = f"{Logfolder}{Name}/{datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log"

        LOG_INFO(f"Current Backup: {Name}", Logging_Folder_Filename, LogLevel)

        if active:
            os.environ["BORG_PASSPHRASE"] = backup["EncryptionPwd"]

            if Initialized:
                LOG_INFO("The repo is initialized.", Logging_Folder_Filename, LogLevel)
                borg_create(json_data["General"], backup, Logging_Folder_Filename)
            elif Initialized == False:
                LOG_INFO(
                    "The repo isn't currently initialized.",
                    Logging_Folder_Filename,
                    LogLevel,
                )
                borg_init(json_data["General"], backup, Logging_Folder_Filename)
        else:
            Mail_warn = True
            MailMessage = f"Backup '{Name}' is not active."
            LOG_WARNING(MailMessage, Logging_Folder_Filename, LogLevel)
    except Exception as e:
        Mail_err = True
        MailMessage = (
            f"There were a unhandled Error while Backing up '{Name}':\t{e.args[0]}"
        )
        LOG_ERROR(MailMessage, Logging_Folder_Filename, LogLevel)
    finally:
        LOG_INFO(f"Backup '{Name}' done.", Logging_Folder_Filename, LogLevel)
        LOG_INFO("--------------------------------", Logging_Folder_Filename, LogLevel)
        os.environ["BORG_PASSPHRASE"] = (
            "We are the Borg. Lower your shields and surrender your ships. We will add your biological and technological distinctiveness to our own. Your culture will adapt to service us. Resistance is futile."
        )

        SendMail_Success = json_data["SMTP"]["SendMailOn"]["Success"]
        SendMail_Warning = json_data["SMTP"]["SendMailOn"]["Warning"]
        SendMail_Error = json_data["SMTP"]["SendMailOn"]["Error"]

        if Mail_succ and SendMail_Success:
            MailMessage = (
                f"Backup was successful.\n"
                f"-        Name:\t{returnjson["archive"]["name"]}\n"
                f"- Remote Repo:\t{returnjson["repository"]["location"]}\n"
                f"-          ID:\t{returnjson["archive"]["id"]}\n"
                f"-       Start:\t{returnjson["archive"]["start"]}\n"
                f"-         End:\t{returnjson["archive"]["end"]}\n"
                f"-    Duration:\t{returnjson["archive"]["duration"]}\n"
                f"Affected Files:\n"
                "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags\n"
            )

            for x in FileArray:
                if x == "":
                    continue

                MailMessage += f"- {x}\n"

            Mail_status = "Successful"
        elif Mail_warn and SendMail_Warning:
            Mail_status = "Warning"
        elif Mail_err and SendMail_Error:
            Mail_status = "Error"

        if True in (SendMail_Success, SendMail_Warning, SendMail_Error):
            MailMessage = MailMessage.replace("\n\n", "\n")
            send_mail(
                json_data["SMTP"],
                Name,
                MailMessage,
                Mail_status,
            )
