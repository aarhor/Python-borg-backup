import json
import subprocess
import os
import sys
import datetime
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
LogLevel = json_data["General"]["LogLevel"]

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

        LOG_INFO(f"Current Backup: {Name}", Logging_Folder_Filename, LogLevel)

        if active:
            os.environ["BORG_PASSPHRASE"] = x["EncryptionPwd"]

            if Initialized:
                LOG_INFO("The repo is initialized.", Logging_Folder_Filename, LogLevel)

                Args_process = [
                    "borg",
                    "create",
                    "--json",
                    "--list",
                    f"{RemoteRepo}::{ArchiveName}",
                    SourcePath,
                ]

                if len(x["Exclude"]) >= 1:
                    for y in x["Exclude"]:
                        Args_process.append("--exclude")
                        Args_process.append(y.replace("{$SourcePath}", SourcePath))

                used_command = ""
                for y in Args_process:
                    used_command += f"{y} "

                LOG_DEBUG(
                    f"borg command: {used_command}",
                    Logging_Folder_Filename,
                    LogLevel,
                )

                proc = subprocess.run(
                    Args_process,
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
                        duration = str(
                            datetime.timedelta(
                                seconds=returnjson["archive"]["duration"]
                            )
                        )[:-3]

                        LOG_INFO(
                            "Backup was successful.", Logging_Folder_Filename, LogLevel
                        )
                        LOG_INFO(
                            f"-        Name:\t{returnjson["archive"]["name"]}",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_INFO(
                            f"- Remote Repo:\t{returnjson["repository"]["location"]}",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_INFO(
                            f"-          ID:\t{returnjson["archive"]["id"]}",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_INFO(
                            f"-       Start:\t{returnjson["archive"]["start"]}",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_INFO(
                            f"-         End:\t{returnjson["archive"]["end"]}",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_INFO(
                            f"-    Duration:\t{duration}",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_DEBUG(f"Affected Files:", Logging_Folder_Filename, LogLevel)
                        LOG_DEBUG(
                            "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags #--",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        for y in FileArray:
                            if y == "":
                                continue

                            LOG_DEBUG(f"- {y}", Logging_Folder_Filename, LogLevel)

                        proc = subprocess.run(
                            [
                                "borg",
                                "prune",
                                f"--keep-daily={str(x["Cleanup"]["daily"])}",
                                f"--keep-monthly={str(x["Cleanup"]["monthly"])}",
                                f"--keep-yearly={str(x["Cleanup"]["yearly"])}",
                                "--list",
                                "--stats",
                                f"{RemoteRepo}",
                            ],
                            capture_output=True,
                        )

                        returnstats = proc.stderr.decode().split("\n")

                        for y in returnstats:
                            if y == "":
                                continue

                            LOG_INFO(y, Logging_Folder_Filename, LogLevel)

                        LOG_DEBUG(
                            f'borg command: borg compact "{RemoteRepo}"',
                            Logging_Folder_Filename,
                            LogLevel,
                        )

                        subprocess.run(
                            [
                                "borg",
                                "compact",
                                f"{RemoteRepo}",
                            ],
                        )

                        LOG_INFO(
                            "Backup Cleanup successful. See the Debug message for more information.",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                    case 1:
                        Mail_warn = True
                        MailMessage = (
                            "Backup was successful, but there were some warnings."
                        )
                        LOG_WARNING(MailMessage, Logging_Folder_Filename, LogLevel)
                    case 2:
                        Mail_err = True
                        MailMessage = f"The Backup wasn't successful, there were a fatal error.\n\t{return_stderr}"
                        LOG_ERROR(
                            "The Backup wasn't successful, there were a fatal error.",
                            Logging_Folder_Filename,
                            LogLevel,
                        )
                        LOG_ERROR(
                            f"\t{return_stderr}", Logging_Folder_Filename, LogLevel
                        )
            elif Initialized == False:
                LOG_INFO(
                    "The repo isn't currently initialized.",
                    Logging_Folder_Filename,
                    LogLevel,
                )
                LOG_DEBUG(
                    f'borg command: borg init --make-parent-dirs --encryption=repokey "{RemoteRepo}"',
                    Logging_Folder_Filename,
                    LogLevel,
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
                LOG_INFO(
                    "--------------------------------",
                    Logging_Folder_Filename,
                    LogLevel,
                )

                for x in InitArray:
                    LOG_INFO(
                        x.replace(
                            " REPOSITORY encrypted", f' "{RemoteRepo}" encrypted'
                        ),
                        Logging_Folder_Filename,
                        LogLevel,
                    )

                LOG_INFO(
                    "--------------------------------",
                    Logging_Folder_Filename,
                    LogLevel,
                )
                LOG_INFO(
                    "The repo is now initialized. Please set the value 'Repo_Initialized' in the config to the value 'true'.",
                    Logging_Folder_Filename,
                    LogLevel,
                )
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
