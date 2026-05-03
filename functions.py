import json
import subprocess
from datetime import datetime, timedelta
import re
from Logging import *
from pathlib import Path


def borg_init(json_data, json_data_current_backup, Logging_file, Only_init):
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)

    if (
        json_data_current_backup["EncryptionPwd"] == "supersecurePassword1337"
        or json_data_current_backup["EncryptionPwd"] == "anothersupersecurePassword420"
        or json_data_current_backup["EncryptionPwd"] == ""
    ):
        LOG_ERROR(
            "You shall not pass!",
            Logging_file,
            json_data,
        )
        LOG_ERROR(
            "Using the default password or a blank password is insecure. Change it in the JSON configuration file.",
            Logging_file,
            json_data,
        )

        return 2
    else:
        Args_process = [
            "borg",
            "init",
            "--make-parent-dirs",
            "--encryption=repokey",
            f"{RemoteRepo}",
        ]

        proc = execute_write_command(Args_process, Logging_file, json_data)
        output_init = proc.stderr.decode()
        returncode = proc.returncode
        InitArray = output_init.split("\n")

        match returncode:
            case 0:
                LOG_INFO(
                    "--------------------------------",
                    Logging_file,
                    json_data,
                )

                for x in InitArray:
                    LOG_INFO(
                        x.replace(
                            " REPOSITORY encrypted", f' "{RemoteRepo}" encrypted'
                        ),
                        Logging_file,
                        json_data,
                    )

                LOG_INFO(
                    "--------------------------------",
                    Logging_file,
                    json_data,
                )
                LOG_INFO(
                    "The repository is now initialized. Please set the value 'Repo_Initialized' to 'true' in the configuration.",
                    Logging_file,
                    json_data,
                )

                if Only_init == False:
                    LOG_INFO(
                        "The first backup will now be made.",
                        Logging_file,
                        json_data,
                    )

                    returnfunc = borg_create(
                        json_data, json_data_current_backup, Logging_file
                    )
                    returnfunc[1]

                    return returnfunc[0]
                else:
                    LOG_INFO(
                        "Due to the parameter '--repo_init', no initial backup was created.",
                        Logging_file,
                        json_data,
                    )
                    return 0
            case 2:
                LOG_ERROR(
                    "An error occurred.",
                    Logging_file,
                    json_data,
                )
                LOG_ERROR(
                    f"\t{output_init}",
                    Logging_file,
                    json_data,
                )

                return 2


def borg_create(json_data, json_data_current_backup, Logging_file):
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

        execute_write_command(Args_process, Logging_file, json_data, "Pre Backup")
        LOG_INFO("Pre Backup command executed", Logging_file, json_data)

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
            LOG_FATAL(
                f"The source path {SourcePath} does not exist!", Logging_file, json_data
            )
            return 3

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

    proc = execute_write_command(Args_process, Logging_file, json_data)
    returncode = proc.returncode
    return_stderr = proc.stderr.decode()
    return_stdout = proc.stdout.decode()

    if Post_BackupCommand != "":
        Args_process = Post_BackupCommand.split(";")

        execute_write_command(Args_process, Logging_file, json_data, "Post Backup")
        LOG_INFO("Post Backup command executed", Logging_file, json_data)

    match returncode:
        case 0:
            FileArray = return_stderr.split("\n")
            if json_data_current_backup["dry_run"] == False:
                returnjson = json.loads(return_stdout)
                duration = str(timedelta(seconds=returnjson["archive"]["duration"]))[
                    :-3
                ]

                LOG_INFO("Backup was successful.", Logging_file, json_data)
                LOG_INFO(
                    f"-        Name:\t{returnjson["archive"]["name"]}",
                    Logging_file,
                    json_data,
                )
                LOG_INFO(
                    f"- Remote Repo:\t{returnjson["repository"]["location"]}",
                    Logging_file,
                    json_data,
                )
                LOG_INFO(
                    f"-          ID:\t{returnjson["archive"]["id"]}",
                    Logging_file,
                    json_data,
                )
                LOG_INFO(
                    f"-       Start:\t{returnjson["archive"]["start"][:-7]}",
                    Logging_file,
                    json_data,
                )
                LOG_INFO(
                    f"-         End:\t{returnjson["archive"]["end"][:-7]}",
                    Logging_file,
                    json_data,
                )
                LOG_INFO(
                    f"-    Duration:\t{duration}",
                    Logging_file,
                    json_data,
                )
                LOG_DEBUG(f"Affected Files:", Logging_file, json_data)
                LOG_DEBUG(
                    "-- For Information about the meaning of the letters see the documentation: https://borgbackup.readthedocs.io/en/stable/usage/create.html#item-flags --",
                    Logging_file,
                    json_data,
                )
                for y in FileArray:
                    if y == "":
                        continue

                    LOG_DEBUG(f"- {y}", Logging_file, json_data)

                borg_prune(json_data, json_data_current_backup, Logging_file)

                LOG_DEBUG(
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

                LOG_INFO(
                    "Backup Cleanup successful.",
                    Logging_file,
                    json_data,
                )

                borg_info(json_data, json_data_current_backup, Logging_file)
            else:
                LOG_INFO("Affected Files:", Logging_file, json_data)
                for y in FileArray:
                    if y == "":
                        continue
                    LOG_INFO(y, Logging_file, json_data)

            return 0
        case 1:
            returnMessage = return_stderr.split("\n")
            LOG_WARNING(
                "Backup was successful, but there were some warnings.",
                Logging_file,
                json_data,
            )

            for y in returnMessage:
                if y == "":
                    continue

                LOG_WARNING(y, Logging_file, json_data)

            return 1
        case 2:
            returnMessage = return_stderr.split("\n")
            LOG_ERROR(
                "The Backup wasn't successful, there were a fatal error.",
                Logging_file,
                json_data,
            )
            for y in returnMessage:
                if y == "":
                    continue

                LOG_ERROR(f"\t{y}", Logging_file, json_data)

            return 2


def borg_prune(json_data, json_data_current_backup, Logging_file):
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

    proc = execute_write_command(Args_process, Logging_file, json_data)
    returnstats = proc.stderr.decode().split("\n")

    for y in returnstats:
        if y == "":
            continue

        LOG_INFO(y, Logging_file, json_data)

    return 0


def borg_check(json_data, json_data_current_backup, Logging_file, sys_args):
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    today = datetime.now()

    Args_process = [
        "borg",
        "check",
        f"{RemoteRepo}",
    ]

    if "--verify-data" in sys_args:
        Args_process.insert(2, "--verify-data")
    else:
        if today.strftime("%d") == "01":
            Args_process.insert(2, "--verify-data")
        else:
            CalendarWeek = int(today.strftime("%V"))

            if CalendarWeek % 2 == 0:
                Args_process.insert(2, "--repository-only")
            else:
                Args_process.insert(2, "--archives-only")

    proc = execute_write_command(Args_process, Logging_file, json_data)
    returnstats = proc.stderr.decode().split("\n")
    returncode = proc.returncode

    match (returncode):
        case 0:
            LOG_INFO(f"Repo {Name} has no errors.", Logging_file, json_data)
            returncode_func = 0
        case 1:
            for y in returnstats:
                if y == "":
                    continue

                LOG_FATAL(y, Logging_file, json_data)
            returncode_func = 3
        case 2:
            for y in returnstats:
                if y == "":
                    continue

                LOG_ERROR(y, Logging_file, json_data)
            returncode_func = 2

    return returncode_func


def borg_key_export(json_data):
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

        LOG_INFO(f"Key export of {Name}.", Logging_file, json_data)
        LOG_INFO(f"\t{Export_filename}", Logging_file, json_data)

        os.environ["BORG_PASSPHRASE"] = backup["EncryptionPwd"]
        os.environ["BORG_RELOCATED_REPO_ACCESS_IS_OK"] = json_data["General"][
            "Allow Relocated Repos"
        ]

        execute_write_command(Args_process, Logging_file, json_data)

        # Read in the file
        with open(Export_filename, "r") as file:
            filedata = file.read()

        # Replace the target string
        filedata = filedata.replace("/path/to/repo", f'"{RemoteRepo}"')
        filedata = filedata.replace("key use borg key", f"key use:\nborg key")

        # Write the file out again
        with open(Export_filename, "w") as file:
            file.write(filedata)

    LOG_INFO("Key export was successful.", Logging_file, json_data)

    return 0


def borg_info(json_data, json_data_current_backup, Logging_file):
    Name = json_data_current_backup["Name"]
    RemoteRepo = json_data_current_backup["RemoteRepo"].replace("{$Name}", Name)
    Args_process = [
        "borg",
        "info",
        "--json",
        f"{RemoteRepo}",
        "--last",
        "1",
    ]

    os.environ["BORG_PASSPHRASE"] = json_data_current_backup["EncryptionPwd"]

    proc = execute_write_command(Args_process, Logging_file, json_data)
    return_stdout = proc.stdout.decode()

    with open(f"{os.path.dirname(Logging_file)}/stats_last.json", "w") as file:
        file.write(return_stdout)

    Args_process.pop(4)
    Args_process.pop(4)

    proc = execute_write_command(Args_process, Logging_file, json_data)
    return_stdout = proc.stdout.decode()

    with open(f"{os.path.dirname(Logging_file)}/stats.json", "w") as file:
        file.write(return_stdout)

    return 0


def execute_write_command(Args, Logging_file, json_data, command_type="borg"):
    used_command = ""

    for y in Args:
        if y == "":
            continue

        used_command += f"{y} "

    LOG_DEBUG(f"{command_type} command: {used_command}", Logging_file, json_data)

    proc = subprocess.run(Args, capture_output=True)

    return proc


def list_all_backups(json_data):
    from prettytable import PrettyTable

    Logfolder = json_data["General"]["Logging"]["Logfolder"]
    table = PrettyTable()
    table.field_names = [
        "Name",
        "Active",
        "Last Run",
        "Files",
        "Size (Total)",
        "Bytes Size",
    ]

    for backup in json_data["backup"]:
        data = []
        Name = backup["Name"]
        file_stats_last = f"{Logfolder}{Name}/stats_last.json"
        file_stats = f"{Logfolder}{Name}/stats.json"

        with open(file_stats_last, "r") as file:
            json_data_last = json.load(file)

        with open(file_stats, "r") as file:
            json_data_repo = json.load(file)

        number_of_files = json_data_last["archives"][0]["stats"]["nfiles"]
        size = int(json_data_repo["cache"]["stats"]["unique_csize"])
        size_string = convert_data_unit(size)

        date_string = (
            json_data_repo["repository"]["last_modified"]
            .replace(".000000", "")
            .replace("T", " ")
        )
        date_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

        data.append(Name)
        data.append(backup["active"])
        data.append(date_object)
        data.append(number_of_files)
        data.append(size_string)
        data.append(size)

        table.add_row(data)

    table.align = "l"
    table.align["Size (Total)"] = "r"
    table.align["Files"] = "r"
    print(
        table.get_string(
            sortby="Bytes Size",
            reversesort=True,
            fields=["Name", "Active", "Last Run", "Files", "Size (Total)"],
        )
    )


def convert_data_unit(size):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size < 1000:
            return f"{size:.2f} {unit}"
        size /= 1000
