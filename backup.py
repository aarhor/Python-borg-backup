import json
import subprocess
import os
import sys
from smtp import *
from Logging import *

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

for x in json_data["backup"]:
    Mail_succ = False
    Mail_warn = False
    Mail_err = False

    try:
        Name = x["Name"]
        active = x["active"]
        Initialized = x["Repo_Initialized"]
        RemoteRepo = x["RemoteRepo"].replace("{$Name}", Name)
        ArchiveName = x["ArchiveName"].replace("$Timestamp", Timestamp)
        SourcePath = x["SourcePath"]
        Logging_Folder_Filename = f"{Logfolder}{Name}/{datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log"

        LOG_INFO(f"Current Backup: {Name}", Logging_Folder_Filename)

        if active:
            os.environ["BORG_PASSPHRASE"] = x["EncryptionPwd"]

            if Initialized:
                LOG_INFO("The repo is initialized.", Logging_Folder_Filename)
                proc = subprocess.run(
                    [
                        "borg",
                        "create",
                        "--json",
                        "--list",
                        f"{RemoteRepo}::{ArchiveName}",
                        SourcePath,
                    ],
                    capture_output=True,
                )
                returncode = proc.returncode
                return_stderr = proc.stderr.decode()
                return_stdout = proc.stdout.decode()
                match returncode:
                    case 0:
                        returnjson = json.loads(return_stdout)
                        FileArray = return_stderr.split("\n")
                        Mail_succ = True

                        LOG_INFO("Backup was successful.", Logging_Folder_Filename)
                        LOG_INFO(
                            f"-     Name:\t{returnjson["archive"]["name"]}",
                            Logging_Folder_Filename,
                        )
                        LOG_INFO(
                            f"-       ID:\t{returnjson["archive"]["id"]}",
                            Logging_Folder_Filename,
                        )
                        LOG_INFO(
                            f"-    Start:\t{returnjson["archive"]["start"]}",
                            Logging_Folder_Filename,
                        )
                        LOG_INFO(
                            f"-      End:\t{returnjson["archive"]["end"]}",
                            Logging_Folder_Filename,
                        )
                        LOG_INFO(
                            f"- Duration:\t{returnjson["archive"]["duration"]}",
                            Logging_Folder_Filename,
                        )
                        LOG_INFO(f"Affected Files:", Logging_Folder_Filename)
                        LOG_INFO(
                            "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags --",
                            Logging_Folder_Filename,
                        )

                        for x in FileArray:
                            if x == "":
                                continue

                            LOG_INFO(f"- {x}", Logging_Folder_Filename)
                    case 1:
                        Mail_warn = True
                        MailMessage = (
                            "Backup was successful, but there were some warnings."
                        )
                        LOG_WARNING(
                            MailMessage,
                            Logging_Folder_Filename,
                        )
                    case 2:
                        Mail_err = True
                        MailMessage = f"The Backup wasn't successful, there were a fatal error.\n\t{return_stderr}"
                        LOG_ERROR(
                            "The Backup wasn't successful, there were a fatal error.",
                            Logging_Folder_Filename,
                        )
                        LOG_ERROR(f"\t{return_stderr}", Logging_Folder_Filename)
            elif Initialized == False:
                LOG_INFO(
                    "The repo isn't currently initialized.", Logging_Folder_Filename
                )
                proc = subprocess.run(
                    [
                        "borg",
                        "init",
                        "--make-parent-dirs",
                        "--encryption=repokey",
                        f"{RemoteRepo}",
                    ],
                    capture_output=True,
                )
                output_init = proc.stderr.decode()

                InitArray = output_init.split("\n")
                LOG_INFO("--------------------------------", Logging_Folder_Filename)

                for x in InitArray:
                    LOG_INFO(x, Logging_Folder_Filename)

                LOG_INFO("--------------------------------", Logging_Folder_Filename)
                LOG_INFO(
                    "The repo is now initialized. Please set the value 'Repo_Initialized' in the config to the value 'true'.",
                    Logging_Folder_Filename,
                )
        else:
            Mail_warn = True
            MailMessage = f"Backup '{Name}' is not active."
            LOG_WARNING(MailMessage, Logging_Folder_Filename)
    except Exception as e:
        Mail_err = True
        MailMessage = (
            f"There were a unhandled Error while Backing up '{Name}':\t{e.args[0]}"
        )
        LOG_ERROR(
            MailMessage,
            Logging_Folder_Filename,
        )
    finally:
        LOG_INFO(f"Backup '{Name}' done.", Logging_Folder_Filename)
        LOG_INFO("--------------------------------", Logging_Folder_Filename)

        if Mail_succ:
            if json_data["SMTP"]["SendMailOn"]["Success"]:
                MailMessage = (
                    f"Backup was successful.\n"
                    f"-     Name:\t{returnjson["archive"]["name"]}\n"
                    f"-       ID:\t{returnjson["archive"]["id"]}\n"
                    f"-    Start:\t{returnjson["archive"]["start"]}\n"
                    f"-      End:\t{returnjson["archive"]["end"]}\n"
                    f"- Duration:\t{returnjson["archive"]["duration"]}\n"
                    f"Affected Files:\n"
                    "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags\n"
                )

                for x in FileArray:
                    if x == "":
                        continue

                    MailMessage += f"- {x}\n"

                send_mail(
                    json_data["SMTP"],
                    Name,
                    MailMessage,
                    "Successful",
                )
        elif Mail_warn:
            if json_data["SMTP"]["SendMailOn"]["Warning"]:
                send_mail(
                    json_data["SMTP"],
                    Name,
                    MailMessage,
                    "Warning",
                )
        elif Mail_err:
            if json_data["SMTP"]["SendMailOn"]["Error"]:
                send_mail(
                    json_data["SMTP"],
                    Name,
                    MailMessage,
                    "Error",
                )
