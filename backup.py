import json
import subprocess
import os
from smtp import *

with open(
    f"{os.path.dirname(os.path.abspath(__file__))}/config/config.json", "r"
) as file:
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
                    "--json",
                    f"{x["RemoteRepo"]}::{ArchiveName}",
                    SourcePath,
                ],
                capture_output=True,
            )
            returncode = proc.returncode
            returnmessage_Error = proc.stderr.decode()
            returnmessage_Successful = proc.stdout.decode()

            match returncode:
                case 0:
                    print("Backup was successful.")

                    if json_data["SMTP"]["SendMailWhenSuccessful"] == True:
                        send_mail(
                            json_data["SMTP"],
                            Name,
                            returnmessage_Successful,
                            "Successful",
                        )
                case 1:
                    print("Backup was successful, but there were some warnings.")
                case 2:
                    print("The Backup wasn't successful, there were a fatal error.")

                    if json_data["SMTP"]["SendMailOnError"] == True:
                        send_mail(json_data["SMTP"], Name, returnmessage_Error, "Error")
        else:
            print("The repo isn't currently initialized.")
            subprocess.run(
                ["borg", "init", "--encryption=repokey", f"{x["RemoteRepo"]}"]
            )
            print(
                "The repo is now initialized. Please set the value 'Repo_Initialized' in the config to the value 'true'."
            )
    else:
        print(f"Backup '{Name}' is not active.")
