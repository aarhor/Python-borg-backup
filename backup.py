import json
import subprocess
import os

with open("config/config.json", "r") as file:
    json_data = json.load(file)

Logfolder = json_data["Logfolder"]
Timestamp = json_data["Timestamp"]
ARGS_create = json_data["ARGS_create"]

for x in json_data["backup"]:
    Name = x["Name"]
    active = x["active"]
    Initialized = x["Repo_Initialized"]
    RemoteRepo = x["RemoteRepo"]

    if active:
        os.environ["BORG_PASSPHRASE"] = x["EncryptionPwd"]

        if Initialized:
            print("The repo is initialized.")
        else:
            print("The repo isn't currently initialized.")
            subprocess.run(
                ["borg", "init", "--encryption=repokey", f"{x["RemoteRepo"]}"]
            )
    else:
        print(f"{Name} is not active")
