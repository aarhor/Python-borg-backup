import json
import subprocess
import datetime
from smtp import *
from Logging import *
from pathlib import Path


def borg_init(json_data, json_data_current_backup, Logging_file):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    LogLevel = json_data["General"]["LogLevel"]

    if (
        json_data_current_backup["EncryptionPwd"] == "supersecurePassword1337"
        or json_data_current_backup["EncryptionPwd"] == "anothersupersecurePassword420"
        or json_data_current_backup["EncryptionPwd"] == ""
    ):
        MailMessage_return += LOG_ERROR(
            "You shall not pass!",
            Logging_file,
            LogLevel,
        )
        MailMessage_return += LOG_ERROR(
            "It's not secure to use the default example password or an empty password. Change it in the json config file.",
            Logging_file,
            LogLevel,
        )

        return 2, MailMessage_return
    else:
        Args_process = [
            "borg",
            "init",
            "--make-parent-dirs",
            "--encryption=repokey",
            f"{RemoteRepo}",
        ]

        used_command = ""
        for y in Args_process:
            if y == "":
                continue

            used_command += f"{y} "

        MailMessage_return += LOG_DEBUG(
            f"borg command: {used_command}",
            Logging_file,
            LogLevel,
        )

        proc = subprocess.run(
            Args_process,
            capture_output=True,
        )

        output_init = proc.stderr.decode()
        returncode = proc.returncode
        InitArray = output_init.split("\n")
        match returncode:
            case 0:
                MailMessage_return += LOG_INFO(
                    "--------------------------------",
                    Logging_file,
                    LogLevel,
                )

                for x in InitArray:
                    MailMessage_return += LOG_INFO(
                        x.replace(
                            " REPOSITORY encrypted", f' "{RemoteRepo}" encrypted'
                        ),
                        Logging_file,
                        LogLevel,
                    )

                MailMessage_return += LOG_INFO(
                    "--------------------------------",
                    Logging_file,
                    LogLevel,
                )
                MailMessage_return += LOG_INFO(
                    "The repo is now initialized. Please set the value 'Repo_Initialized' in the config to the value 'true'.",
                    Logging_file,
                    LogLevel,
                )
                MailMessage_return += LOG_INFO(
                    "The first backup will now be made.",
                    Logging_file,
                    LogLevel,
                )

                returnfunc = borg_create(
                    json_data, json_data_current_backup, Logging_file
                )
                MailMessage_return += returnfunc[1]

                return returnfunc[0], MailMessage_return
            case 2:
                MailMessage_return += LOG_ERROR(
                    "An error occurred.",
                    Logging_file,
                    LogLevel,
                )
                MailMessage_return += LOG_ERROR(
                    f"\t{output_init}",
                    Logging_file,
                    LogLevel,
                )

                return 2, MailMessage_return


def borg_create(json_data, json_data_current_backup, Logging_file):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    ArchiveName = json_data_current_backup["ArchiveName"].replace(
        "$Timestamp", json_data["General"]["Timestamp"]
    )
    SourcePath = Path(json_data_current_backup["SourcePath"])
    LogLevel = json_data["General"]["LogLevel"]

    if SourcePath.exists():
        Args_process = [
            "borg",
            "create",
            "--list",
            "--json",
            f"{RemoteRepo}::{ArchiveName}",
            SourcePath,
        ]

        if json_data_current_backup["dry_run"]:
            Args_process.insert(4, "--dry-run")

        if len(json_data_current_backup["Exclude"]) >= 1:
            for y in json_data_current_backup["Exclude"]:
                Args_process.insert(4, "--exclude")
                Args_process.insert(5, y.replace("{$SourcePath}", SourcePath))

        used_command = ""
        for y in Args_process:
            if y == "":
                continue

            used_command += f"{y} "

        MailMessage_return += LOG_DEBUG(
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
                FileArray = return_stderr.split("\n")
                if json_data_current_backup["dry_run"] == False:
                    returnjson = json.loads(return_stdout)
                    duration = str(
                        datetime.timedelta(seconds=returnjson["archive"]["duration"])
                    )[:-3]

                    MailMessage_return += LOG_INFO(
                        "Backup was successful.", Logging_file, LogLevel
                    )
                    MailMessage_return += LOG_INFO(
                        f"-        Name:\t{returnjson["archive"]["name"]}",
                        Logging_file,
                        LogLevel,
                    )
                    MailMessage_return += LOG_INFO(
                        f"- Remote Repo:\t{returnjson["repository"]["location"]}",
                        Logging_file,
                        LogLevel,
                    )
                    MailMessage_return += LOG_INFO(
                        f"-          ID:\t{returnjson["archive"]["id"]}",
                        Logging_file,
                        LogLevel,
                    )
                    MailMessage_return += LOG_INFO(
                        f"-       Start:\t{returnjson["archive"]["start"][:-7]}",
                        Logging_file,
                        LogLevel,
                    )
                    MailMessage_return += LOG_INFO(
                        f"-         End:\t{returnjson["archive"]["end"][:-7]}",
                        Logging_file,
                        LogLevel,
                    )
                    MailMessage_return += LOG_INFO(
                        f"-    Duration:\t{duration}",
                        Logging_file,
                        LogLevel,
                    )
                    MailMessage_return += LOG_DEBUG(
                        f"Affected Files:", Logging_file, LogLevel
                    )
                    MailMessage_return += LOG_DEBUG(
                        "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags --",
                        Logging_file,
                        LogLevel,
                    )
                    for y in FileArray:
                        if y == "":
                            continue

                        MailMessage_return += LOG_DEBUG(
                            f"- {y}", Logging_file, LogLevel
                        )

                    returnfunc = borg_prune(
                        json_data, json_data_current_backup, Logging_file
                    )

                    MailMessage_return += returnfunc[1]

                    MailMessage_return += LOG_DEBUG(
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

                    MailMessage_return += LOG_INFO(
                        "Backup Cleanup successful.",
                        Logging_file,
                        LogLevel,
                    )
                else:
                    MailMessage_return += LOG_INFO(
                        "Affected Files:", Logging_file, LogLevel
                    )
                    for y in FileArray:
                        if y == "":
                            continue
                        MailMessage_return += LOG_INFO(y, Logging_file, LogLevel)

                return 0, MailMessage_return
            case 1:
                returnMessage = return_stderr.split("\n")
                MailMessage_return += LOG_WARNING(
                    "Backup was successful, but there were some warnings.",
                    Logging_file,
                    LogLevel,
                )

                for y in returnMessage:
                    if y == "":
                        continue

                    MailMessage_return += LOG_WARNING(y, Logging_file, LogLevel)

                return 1, MailMessage_return
            case 2:
                returnMessage = return_stderr.split("\n")
                MailMessage_return += LOG_ERROR(
                    "The Backup wasn't successful, there were a fatal error.",
                    Logging_file,
                    LogLevel,
                )
                for y in returnMessage:
                    if y == "":
                        continue

                    MailMessage_return += LOG_ERROR(f"\t{y}", Logging_file, LogLevel)

                return 2, MailMessage_return
    else:
        MailMessage_return += LOG_FATAL(
            f"The source path {SourcePath} does not exist!", Logging_file, LogLevel
        )
        return 3, MailMessage_return


def borg_prune(json_data, json_data_current_backup, Logging_file):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    LogLevel = json_data["General"]["LogLevel"]
    Args_process = [
        "borg",
        "prune",
        f"--keep-daily={str(json_data_current_backup["Cleanup"]["daily"])}",
        f"--keep-monthly={str(json_data_current_backup["Cleanup"]["monthly"])}",
        f"--keep-yearly={str(json_data_current_backup["Cleanup"]["yearly"])}",
        "--list",
        "--stats",
        f"{RemoteRepo}",
    ]

    used_command = ""
    for y in Args_process:
        if y == "":
            continue

        used_command += f"{y} "

    MailMessage_return += LOG_DEBUG(
        f"borg command: {used_command}",
        Logging_file,
        LogLevel,
    )

    proc = subprocess.run(
        Args_process,
        capture_output=True,
    )

    returnstats = proc.stderr.decode().split("\n")

    for y in returnstats:
        if y == "":
            continue

        MailMessage_return += LOG_INFO(y, Logging_file, LogLevel)

    return 0, MailMessage_return
