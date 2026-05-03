import json
import os
import sys
import shutil
from datetime import datetime
import traceback
import socket
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
        BackupStatus = ""

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
            ListforMail.append(Begin.strftime("%Y-%m-%d %H:%M:%S"))

            LOG_INFO(f"Current Backup: {Name}", Logging_Folder_Filename, json_data)

            if active:
                os.environ["BORG_PASSPHRASE"] = backup["EncryptionPwd"]
                os.environ["BORG_RELOCATED_REPO_ACCESS_IS_OK"] = json_data["General"][
                    "Allow Relocated Repos"
                ]

                if Initialized and Only_Init:
                    LOG_INFO(
                        "Due to the parameter '--repo_init' and because it is already initialized, this backup was skipped.",
                        Logging_Folder_Filename,
                        json_data,
                    )
                    returnfunc = [0]
                    BackupStatus = "🟧 Skipped"
                    continue

                if Initialized:
                    LOG_INFO(
                        "The repo is initialized.", Logging_Folder_Filename, json_data
                    )

                    if "--skip_pre_check" not in sys.argv:
                        returnfunc = borg_check(
                            json_data, backup, Logging_Folder_Filename, sys.argv
                        )
                    else:
                        returnfunc = [0]

                    if returnfunc == 0:
                        returnfunc = borg_create(
                            json_data, backup, Logging_Folder_Filename
                        )
                    else:
                        LOG_ERROR(
                            "Because of an error with the Integrity of the repo, no backup has been made.\nSee the logs for more information.",
                            Logging_Folder_Filename,
                            json_data,
                        )
                        LOG_INFO(
                            f"Backup '{Name}' done with errors.",
                            Logging_Folder_Filename,
                            json_data,
                        )
                        BackupStatus = "🟥 Error"
                elif Initialized == False:
                    LOG_INFO(
                        "The repo isn't currently initialized.",
                        Logging_Folder_Filename,
                        json_data,
                    )
                    returnfunc = borg_init(
                        json_data, backup, Logging_Folder_Filename, Only_Init
                    )
                    LOG_INFO(
                        f"Backup '{Name}' done.",
                        Logging_Folder_Filename,
                        json_data,
                    )
                    BackupStatus = "🟩 Success"
            else:
                LOG_WARNING(
                    f"Backup '{Name}' is not active.",
                    Logging_Folder_Filename,
                    json_data,
                )
                LOG_INFO(
                    f"Backup '{Name}' done with warnings.",
                    Logging_Folder_Filename,
                    json_data,
                )
                BackupStatus = "🟧 Skipped"
                returnfunc = [1]
        except Exception as e:
            LOG_FATAL(
                f"There were a unhandled Error while Backing up '{Name}':",
                Logging_Folder_Filename,
                json_data,
            )
            LOG_FATAL(
                f"\t{e.args[0]}",
                Logging_Folder_Filename,
                json_data,
            )
            LOG_FATAL(
                f"\t{traceback.format_exc()}",
                Logging_Folder_Filename,
                json_data,
            )
            LOG_INFO(
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
                if returnfunc == 0:
                    BackupStatus = "🟩 Success"
                elif returnfunc == 1:
                    BackupStatus = "🟧 Warning"
                elif returnfunc == 2:
                    BackupStatus = "🟥 Error"
                elif returnfunc == 3:
                    BackupStatus = "🟥 Fatal"

            LogRotation(json_data, f"{Logfolder}{Name}")

        file_stats_last = f"{Logfolder}{Name}/stats_last.json"

        with open(file_stats_last, "r") as file:
            json_data_last = json.load(file)

        size = int(json_data_last["cache"]["stats"]["unique_csize"])
        size_string = convert_data_unit(size)

        End = datetime.now()
        TimeSpan = str(End - Begin)[:-7]
        ListforMail.append(End.strftime("%Y-%m-%d %H:%M:%S"))
        ListforMail.append(TimeSpan)
        ListforMail.append(BackupStatus)
        ListforMail.append(size_string)

    Mail_handling(json_data, ListforMail)


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


def Mail_handling(json_data, ListforMail):
    MailMessage = "<html> <h1>Backup Report</h1> <table> <tr> <td><b>Date</b></td> <td>{$Today}</td> </tr> <tr> <td><b>Hostname</b></td> <td>{$Hostname}</td> </tr> </table> <br> <table border='1px solid black'> <tr> <th>Name</th> <th>Active</th> <th>Begin</th> <th>End</th> <th>TimeSpan</th> <th>Status</th> <th>New</th> </tr>{$Data}</table></html>"
    table_data = ""
    MailMessage = MailMessage.replace("{$Today}", datetime.now().strftime("%Y-%m-%d"))
    MailMessage = MailMessage.replace("{$Hostname}", socket.gethostname())

    i = 0
    while i < len(ListforMail):
        table_data += f"<tr><td>{ListforMail[i]}</td> <td>{ListforMail[i+1]}</td> <td>{ListforMail[i+2]}</td> <td>{ListforMail[i+3]}</td> <td>{ListforMail[i+4]}</td> <td>{ListforMail[i+5]}</td> <td align='right'>{ListforMail[i+6]}</td></tr>"
        i += 7

    MailMessage = MailMessage.replace("{$Data}", table_data)

    send_mail(json_data["SMTP"], MailMessage)


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
