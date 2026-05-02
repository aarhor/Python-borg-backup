import json
import os
import sys
import shutil
from datetime import datetime
import traceback
from smtp import *
from Logging import *
from functions import *


def start_backup_routine():
    with open(Path_config, "r") as file:
        json_data = json.load(file)

    Logfolder = json_data["General"]["Logging"]["Logfolder"]

    ListforMail = []

    if "--list" in sys.argv:
        list_all_backups(json_data)
        exit()

    for backup in json_data["backup"]:
        MailMessage = ""
        Name = backup["Name"]
        Logging_Folder_Filename = (
            f"{Logfolder}{Name}/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log"
        )
        Begin = datetime.now()
        BackupStatus = "tmp"

        if Single_Import == True and Name != Single_Import_Name:
            LOG_INFO(f"Skipped backup: {Name}", Logging_Folder_Filename, json_data)
            os.remove(Logging_Folder_Filename)
            BackupStatus = "🟧 Skipped"
            continue

        try:
            active = backup["active"]
            Initialized = backup["Repo_Initialized"]

            ListforMail.append(Name)
            ListforMail.append(
                str(active)
                .lower()
                .replace("true", "Active")
                .replace("false", "Stopped")
            )
            ListforMail.append(Begin.strftime("%Y-%m-%d %H-%M-%S"))

            MailMessage += LOG_INFO(
                f"Current Backup: {Name}", Logging_Folder_Filename, json_data
            )

            if active:
                os.environ["BORG_PASSPHRASE"] = backup["EncryptionPwd"]
                os.environ["BORG_RELOCATED_REPO_ACCESS_IS_OK"] = json_data["General"][
                    "Allow Relocated Repos"
                ]

                if Initialized and Only_Init:
                    MailMessage += LOG_INFO(
                        "Due to the parameter '--repo_init' and because it is already initialized, this backup was skipped.",
                        Logging_Folder_Filename,
                        json_data,
                    )
                    returnfunc = [0]
                    BackupStatus = "🟧 Skipped"
                    continue

                if Initialized:
                    MailMessage += LOG_INFO(
                        "The repo is initialized.", Logging_Folder_Filename, json_data
                    )

                    if "--skip_pre_check" not in sys.argv:
                        returnfunc = borg_check(
                            json_data, backup, Logging_Folder_Filename, sys.argv
                        )
                    else:
                        returnfunc = [0]

                    if returnfunc[0] == 0:
                        returnfunc = borg_create(
                            json_data, backup, Logging_Folder_Filename
                        )
                    else:
                        MailMessage += LOG_ERROR(
                            "Because of an error with the Integrity of the repo, no backup has been made.\nSee the logs for more information.",
                            Logging_Folder_Filename,
                            json_data,
                        )
                        MailMessage += LOG_INFO(
                            f"Backup '{Name}' done with errors.",
                            Logging_Folder_Filename,
                            json_data,
                        )
                        BackupStatus = "🟥 Error"
                elif Initialized == False:
                    MailMessage += LOG_INFO(
                        "The repo isn't currently initialized.",
                        Logging_Folder_Filename,
                        json_data,
                    )
                    returnfunc = borg_init(
                        json_data, backup, Logging_Folder_Filename, Only_Init
                    )
                    MailMessage += LOG_INFO(
                        f"Backup '{Name}' done.",
                        Logging_Folder_Filename,
                        json_data,
                    )
                    BackupStatus = "🟩 Success"

                MailMessage += returnfunc[1]
            else:
                MailMessage += LOG_WARNING(
                    f"Backup '{Name}' is not active.",
                    Logging_Folder_Filename,
                    json_data,
                )
                MailMessage += LOG_INFO(
                    f"Backup '{Name}' done with warnings.",
                    Logging_Folder_Filename,
                    json_data,
                )
                BackupStatus = "🟧 Skipped"
                returnfunc = [1]
        except Exception as e:
            MailMessage += LOG_FATAL(
                f"There were a unhandled Error while Backing up '{Name}':",
                Logging_Folder_Filename,
                json_data,
            )
            MailMessage += LOG_FATAL(
                f"\t{e.args[0]}",
                Logging_Folder_Filename,
                json_data,
            )
            MailMessage += LOG_FATAL(
                f"\t{traceback.format_exc()}",
                Logging_Folder_Filename,
                json_data,
            )
            MailMessage += LOG_INFO(
                f"Backup '{Name}' done with errors.", Logging_Folder_Filename, json_data
            )
            returnfunc = [3]
        finally:
            LOG_INFO(
                "--------------------------------", Logging_Folder_Filename, json_data
            )
            os.environ["BORG_PASSPHRASE"] = (
                "We are the Borg. Lower your shields and surrender your ships. We will add your biological and technological distinctiveness to our own. Your culture will adapt to service us. Resistance is futile."
            )

            if BackupStatus == "":
                if returnfunc[0] == 0:
                    BackupStatus = "🟩 Success"
                elif returnfunc[0] == 1:
                    BackupStatus = "🟧 Warning"
                elif returnfunc[0] == 2:
                    BackupStatus = "🟥 Error"
                elif returnfunc[0] == 3:
                    BackupStatus = "🟥 Fatal"

            LogRotation(json_data, f"{Logfolder}{Name}")

        file_stats_last = f"{Logfolder}{Name}/stats_last.json"

        with open(file_stats_last, "r") as file:
            json_data_last = json.load(file)

        size = int(json_data_last["cache"]["stats"]["unique_csize"])
        size_string = ""

        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1000:
                size_string = f"{size:.2f} {unit}"
                break
            size /= 1000

        End = datetime.now()
        TimeSpan = str(End - Begin)[:-7]
        ListforMail.append(End.strftime("%Y-%m-%d %H-%M-%S"))
        ListforMail.append(TimeSpan)
        ListforMail.append(BackupStatus)
        ListforMail.append(size_string)


def dependency_check():
    with open(Path_config, "r") as file:
        json_data = json.load(file)

    borg_path = shutil.which("borg")
    if borg_path:
        LOG_DEBUG(
            f"BorgBackup binary found in $PATH.",
            "",
            json_data,
        )
        return True
    else:
        LOG_FATAL(
            f"BorgBackup not found. Please use 'sudo apt install borgbackup' or use the instructions on https://borgbackup.readthedocs.io/en/stable/installation.html",
            "",
            json_data,
        )
        return False


def Mail_handling(json_data, MailMessage, returnfunc, Name=""):
    returncode_func = returnfunc[0]
    status_map = {
        0: ("Successful", "Success"),
        1: ("Warning", "Warning"),
        2: ("Error", "Error"),
        3: ("Fatal", "Fatal"),
    }

    if returncode_func in status_map:
        status_text, config_key = status_map[returncode_func]

        if json_data["SMTP"]["SendMailOn"].get(config_key):
            MailMessage = MailMessage.replace("\n\n", "\n")

            send_mail(
                json_data["SMTP"],
                Name,
                MailMessage,
                status_text,
            )


Path_config = f"{os.path.dirname(os.path.abspath(__file__))}/config/config.json"
Only_Init = False
Single_Import = False
Single_Import_Name = ""


i = 0
for arg in sys.argv:
    if arg.startswith("--config_file="):
        Path_config = f"{sys.argv[i].replace("--config_file=", "")}"
    if arg.startswith("--repo_init"):
        Only_Init = True
    if arg.startswith("--key_export"):
        with open(Path_config, "r") as file:
            json_data = json.load(file)

        borg_key_export(json_data)
        exit()
    if arg.startswith("--single_import="):
        Single_Import = True
        Single_Import_Name = (
            f"{sys.argv[i].replace("--single_import=", "").replace("\"","")}"
        )
    i = i + 1

if dependency_check():
    start_backup_routine()
