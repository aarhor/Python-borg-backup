import json
import subprocess
from datetime import datetime, timedelta
import re
from smtp import *
from Logging import *
from pathlib import Path


def borg_init(json_data, json_data_current_backup, Logging_file, Only_init):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)

    if (
        json_data_current_backup["EncryptionPwd"] == "supersecurePassword1337"
        or json_data_current_backup["EncryptionPwd"] == "anothersupersecurePassword420"
        or json_data_current_backup["EncryptionPwd"] == ""
    ):
        MailMessage_return += LOG_ERROR(
            "You shall not pass!",
            Logging_file,
            json_data,
        )
        MailMessage_return += LOG_ERROR(
            "Using the default password or a blank password is insecure. Change it in the JSON configuration file.",
            Logging_file,
            json_data,
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
            f"borg command: {used_command}", Logging_file, json_data
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
                    json_data,
                )

                for x in InitArray:
                    MailMessage_return += LOG_INFO(
                        x.replace(
                            " REPOSITORY encrypted", f' "{RemoteRepo}" encrypted'
                        ),
                        Logging_file,
                        json_data,
                    )

                MailMessage_return += LOG_INFO(
                    "--------------------------------",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_INFO(
                    "The repository is now initialized. Please set the value 'Repo_Initialized' to 'true' in the configuration.",
                    Logging_file,
                    json_data,
                )

                if Only_init == False:
                    MailMessage_return += LOG_INFO(
                        "The first backup will now be made.",
                        Logging_file,
                        json_data,
                    )

                    returnfunc = borg_create(
                        json_data, json_data_current_backup, Logging_file
                    )
                    MailMessage_return += returnfunc[1]

                    return returnfunc[0], MailMessage_return
                else:
                    MailMessage_return += LOG_INFO(
                        "Due to the parameter '--repo_init', no initial backup was created.",
                        Logging_file,
                        json_data,
                    )
                    return 0, MailMessage_return
            case 2:
                MailMessage_return += LOG_ERROR(
                    "An error occurred.",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_ERROR(
                    f"\t{output_init}",
                    Logging_file,
                    json_data,
                )

                return 2, MailMessage_return


def borg_create(json_data, json_data_current_backup, Logging_file):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    ArchiveName = json_data_current_backup["ArchiveName"].replace(
        "$Timestamp", json_data["General"]["Timestamp"]
    )
    SourcePath_list = json_data_current_backup["SourcePath"]
    Pre_BackupCommand = json_data_current_backup["Pre_BackupCommand"]
    Post_BackupCommand = json_data_current_backup["Post_BackupCommand"]

    if Pre_BackupCommand != "":
        Args_process = Pre_BackupCommand.split(";")

        used_command = ""
        for y in Args_process:
            if y == "":
                continue

            used_command += f"{y} "

        MailMessage_return += LOG_DEBUG(
            f"Pre Backup command: {used_command}", Logging_file, json_data
        )

        proc = subprocess.run(Args_process, capture_output=True)

        MailMessage_return += LOG_INFO(
            "Pre Backup command executed", Logging_file, json_data
        )

    Args_process = [
        "borg",
        "create",
        "--list",
        "--json",
        f"{RemoteRepo}::{ArchiveName}",
    ]

    for SourcePath in SourcePath_list:
        if Path(SourcePath).exists():
            Args_process.append(SourcePath)
        else:
            MailMessage_return += LOG_FATAL(
                f"The source path {SourcePath} does not exist!", Logging_file, json_data
            )
            return 3, MailMessage_return

    if json_data_current_backup["dry_run"]:
        Args_process.insert(4, "--dry-run")

    if len(json_data_current_backup["Exclude"]) >= 1:
        for y in json_data_current_backup["Exclude"]:
            ID_SourcePath_match = re.search(r"(?<=\{\$SourcePath)\d+(?=\})", y)

            if ID_SourcePath_match:
                ID_SourcePath = int(ID_SourcePath_match.group(0))

                Args_process.insert(4, "--exclude")
                Args_process.insert(
                    5,
                    y.replace(
                        f"{{$SourcePath{ID_SourcePath}}}",
                        SourcePath_list[ID_SourcePath],
                    ),
                )
            else:
                Args_process.insert(4, "--exclude")
                Args_process.insert(5, y)

    used_command = ""
    for y in Args_process:
        if y == "":
            continue

        used_command += f"{y} "

    MailMessage_return += LOG_DEBUG(
        f"borg command: {used_command}", Logging_file, json_data
    )

    proc = subprocess.run(
        Args_process,
        capture_output=True,
    )
    returncode = proc.returncode
    return_stderr = proc.stderr.decode()
    return_stdout = proc.stdout.decode()

    with open(f"{os.path.dirname(Logging_file)}/stats.json", "w") as file:
        file.write(return_stdout)

    if Post_BackupCommand != "":
        Args_process = Post_BackupCommand.split(";")

        used_command = ""
        for y in Args_process:
            if y == "":
                continue

            used_command += f"{y} "

        MailMessage_return += LOG_DEBUG(
            f"Post Backup command: {used_command}", Logging_file, json_data
        )

        proc = subprocess.run(Args_process, capture_output=True)

        MailMessage_return += LOG_INFO(
            "Post Backup command executed", Logging_file, json_data
        )

    match returncode:
        case 0:
            FileArray = return_stderr.split("\n")
            if json_data_current_backup["dry_run"] == False:
                returnjson = json.loads(return_stdout)
                duration = str(timedelta(seconds=returnjson["archive"]["duration"]))[
                    :-3
                ]

                MailMessage_return += LOG_INFO(
                    "Backup was successful.", Logging_file, json_data
                )
                MailMessage_return += LOG_INFO(
                    f"-        Name:\t{returnjson["archive"]["name"]}",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_INFO(
                    f"- Remote Repo:\t{returnjson["repository"]["location"]}",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_INFO(
                    f"-          ID:\t{returnjson["archive"]["id"]}",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_INFO(
                    f"-       Start:\t{returnjson["archive"]["start"][:-7]}",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_INFO(
                    f"-         End:\t{returnjson["archive"]["end"][:-7]}",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_INFO(
                    f"-    Duration:\t{duration}",
                    Logging_file,
                    json_data,
                )
                MailMessage_return += LOG_DEBUG(
                    f"Affected Files:", Logging_file, json_data
                )
                MailMessage_return += LOG_DEBUG(
                    "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags --",
                    Logging_file,
                    json_data,
                )
                for y in FileArray:
                    if y == "":
                        continue

                    MailMessage_return += LOG_DEBUG(f"- {y}", Logging_file, json_data)

                returnfunc = borg_prune(
                    json_data, json_data_current_backup, Logging_file
                )

                MailMessage_return += returnfunc[1]

                MailMessage_return += LOG_DEBUG(
                    f'borg command: borg compact "{RemoteRepo}"',
                    Logging_file,
                    json_data,
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
                    json_data,
                )
            else:
                MailMessage_return += LOG_INFO(
                    "Affected Files:", Logging_file, json_data
                )
                for y in FileArray:
                    if y == "":
                        continue
                    MailMessage_return += LOG_INFO(y, Logging_file, json_data)

            return 0, MailMessage_return
        case 1:
            returnMessage = return_stderr.split("\n")
            MailMessage_return += LOG_WARNING(
                "Backup was successful, but there were some warnings.",
                Logging_file,
                json_data,
            )

            for y in returnMessage:
                if y == "":
                    continue

                MailMessage_return += LOG_WARNING(y, Logging_file, json_data)

            return 1, MailMessage_return
        case 2:
            returnMessage = return_stderr.split("\n")
            MailMessage_return += LOG_ERROR(
                "The Backup wasn't successful, there were a fatal error.",
                Logging_file,
                json_data,
            )
            for y in returnMessage:
                if y == "":
                    continue

                MailMessage_return += LOG_ERROR(f"\t{y}", Logging_file, json_data)

            return 2, MailMessage_return


def borg_prune(json_data, json_data_current_backup, Logging_file):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
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
        f"borg command: {used_command}", Logging_file, json_data
    )

    proc = subprocess.run(
        Args_process,
        capture_output=True,
    )

    returnstats = proc.stderr.decode().split("\n")

    for y in returnstats:
        if y == "":
            continue

        MailMessage_return += LOG_INFO(y, Logging_file, json_data)

    return 0, MailMessage_return


def borg_check(json_data, json_data_current_backup, Logging_file, sys_args):
    MailMessage_return = ""
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    Args_process = [
        "borg",
        "check",
        f"{RemoteRepo}",
    ]

    if "--verify-data" in sys_args:
        Args_process.insert(2, "--verify-data")

    used_command = ""
    for y in Args_process:
        if y == "":
            continue

        used_command += f"{y} "

    MailMessage_return += LOG_DEBUG(
        f"borg command: {used_command}", Logging_file, json_data
    )

    proc = subprocess.run(
        Args_process,
        capture_output=True,
    )

    returnstats = proc.stderr.decode().split("\n")
    returncode = proc.returncode

    match (returncode):
        case 0:
            MailMessage_return += LOG_INFO(
                f"Repo {Name} has no errors.", Logging_file, json_data
            )
            returncode_func = 0
        case 1:
            for y in returnstats:
                if y == "":
                    continue

                MailMessage_return += LOG_FATAL(y, Logging_file, json_data)
            returncode_func = 3
        case 2:
            for y in returnstats:
                if y == "":
                    continue

                MailMessage_return += LOG_ERROR(y, Logging_file, json_data)
            returncode_func = 2

    return returncode_func, MailMessage_return


def borg_key_export(json_data):
    MailMessage_return = ""
    Logfolder = json_data["General"]["Logging"]["Logfolder"]
    Logging_file = (
        f"{Logfolder}{{Name}}/{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.log"
    )
    all_backups = json_data["backup"]

    for backup in all_backups:
        Name = backup["Name"]
        RemoteRepo = backup["RemoteRepo"]
        Logging_file = Logging_file.replace("{Name}", Name)
        Export_filename = f"{os.path.dirname(os.path.abspath(__file__))}/export/encrypted-key-backup_{Name.replace(" ", "_")}.txt"
        Args_process = [
            "borg",
            "key",
            "export",
            "--paper",
            RemoteRepo,
            Export_filename,
        ]
        MailMessage_return += LOG_INFO(
            f"Key export of {Name}.", Logging_file, json_data
        )
        MailMessage_return += LOG_INFO(f"\t{Export_filename}", Logging_file, json_data)

        os.environ["BORG_PASSPHRASE"] = backup["EncryptionPwd"]
        os.environ["BORG_RELOCATED_REPO_ACCESS_IS_OK"] = json_data["General"][
            "Allow Relocated Repos"
        ]

        used_command = ""
        for y in Args_process:
            if y == "":
                continue

            used_command += f"{y} "

        MailMessage_return += LOG_DEBUG(
            f"borg command: {used_command}", Logging_file, json_data
        )

        subprocess.run(
            Args_process,
            capture_output=True,
        )

        # Read in the file
        with open(Export_filename, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("/path/to/repo", f'"{RemoteRepo}"')
        filedata = filedata.replace("key use borg key", f"key use:\nborg key")

        # Write the file out again
        with open(Export_filename, "w") as file:
            file.write(filedata)

    MailMessage_return += LOG_INFO(
        "Key export was successful.", Logging_file, json_data
    )

    return 0, MailMessage_return
