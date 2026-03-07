import json
import subprocess
import os

with open("config/config.json", "r") as file:
    json_data = json.load(file)

Logfolder = json_data["General"]["Logfolder"]
Timestamp = json_data["General"]["Timestamp"]
ARGS_create = json_data["General"]["ARGS_create"]

for x in json_data["backup"]:
    Name = x["Name"]
    active = x["active"]
    Initialized = x["Repo_Initialized"]
    RemoteRepo = x["RemoteRepo"]
    ArchiveName = x["ArchiveName"].replace("$Timestamp", Timestamp)
    SourcePath = x["SourcePath"]

    if active:
        os.environ["BORG_PASSPHRASE"] = x["EncryptionPwd"]

        if Initialized:
            print("The repo is initialized.")
            proc = subprocess.run(
                [
                    "borg",
                    "create",
                    f"{x["RemoteRepo"]}::{ArchiveName}",
                    SourcePath,
                    "--progress",
                ],
                capture_output=True,
            )

            print(proc.stdout)
        else:
            print("The repo isn't currently initialized.")
            subprocess.run(
                ["borg", "init", "--encryption=repokey", f"{x["RemoteRepo"]}"]
            )
    else:
        print(f"{Name} is not active")
