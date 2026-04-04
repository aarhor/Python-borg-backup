import json
import subprocess
import os
import sys
import datetime
import smtp
import Logging

def borg_create(json_data_general, json_data_current_backup, Logging_file):
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    ArchiveName = json_data_current_backup["ArchiveName"].replace(
        "$Timestamp", json_data_general["Timestamp"]
    )
    SourcePath = json_data_current_backup["SourcePath"]
    LogLevel = json_data_general["LogLevel"]

    Args_process = [
        "borg",
        "create",
        "--json",
        "--list",
        f"{RemoteRepo}::{ArchiveName}",
        SourcePath,
    ]

    if len(json_data_current_backup["Exclude"]) >= 1:
        for y in json_data_current_backup["Exclude"]:
            Args_process.append("--exclude")
            Args_process.append(y.replace("{$SourcePath}", SourcePath))

    used_command = ""
    for y in Args_process:
        if y == "":
            continue

        used_command += f"{y} "

    Logging.LOG_DEBUG(
        f"borg command: {used_command}",
        Logging_file,
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
                Logging.datetime.timedelta(seconds=returnjson["archive"]["duration"])
            )[:-3]

            Logging.LOG_INFO("Backup was successful.", Logging_file, LogLevel)
            Logging.LOG_INFO(
                f"-        Name:\t{returnjson["archive"]["name"]}",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_INFO(
                f"- Remote Repo:\t{returnjson["repository"]["location"]}",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_INFO(
                f"-          ID:\t{returnjson["archive"]["id"]}",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_INFO(
                f"-       Start:\t{returnjson["archive"]["start"][:-7]}",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_INFO(
                f"-         End:\t{returnjson["archive"]["end"][:-7]}",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_INFO(
                f"-    Duration:\t{duration}",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_DEBUG(f"Affected Files:", Logging_file, LogLevel)
            Logging.LOG_DEBUG(
                "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags #--",
                Logging_file,
                LogLevel,
            )
            for y in FileArray:
                if y == "":
                    continue

                Logging.LOG_DEBUG(f"- {y}", Logging_file, LogLevel)

            proc = subprocess.run(
                [
                    "borg",
                    "prune",
                    f"--keep-daily={str(json_data_current_backup["Cleanup"]["daily"])}",
                    f"--keep-monthly={str(json_data_current_backup["Cleanup"]["monthly"])}",
                    f"--keep-yearly={str(json_data_current_backup["Cleanup"]["yearly"])}",
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

                Logging.LOG_INFO(y, Logging_file, LogLevel)

            Logging.LOG_DEBUG(
                f'borg command: borg compact "{RemoteRepo}"',
                Logging_file,
                LogLevel,
            )

            subprocess.run(
                [
                    "borg",
                    "compact",
                    f"{RemoteRepo}",
                ],
            )

            Logging.LOG_INFO(
                "Backup Cleanup successful.",
                Logging_file,
                LogLevel,
            )
        case 1:
            Mail_warn = True
            MailMessage = "Backup was successful, but there were some warnings."
            Logging.LOG_WARNING(MailMessage, Logging_file, LogLevel)
        case 2:
            Mail_err = True
            MailMessage = f"The Backup wasn't successful, there were a fatal error.\n\t{return_stderr}"
            Logging.LOG_ERROR(
                "The Backup wasn't successful, there were a fatal error.",
                Logging_file,
                LogLevel,
            )
            Logging.LOG_ERROR(f"\t{return_stderr}", Logging_file, LogLevel)
