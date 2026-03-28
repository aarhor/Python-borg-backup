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
                    "--list",
                    f"{x["RemoteRepo"]}::{ArchiveName}",
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
                    print("Backup was successful.")
                    print(f"\tArchive Name:\t{returnjson["archive"]["name"]}")
                    print(f"\tID:\t\t{returnjson["archive"]["id"]}")
                    print(f"\tStart:\t\t{returnjson["archive"]["start"]}")
                    print(f"\tEnd:\t\t{returnjson["archive"]["end"]}")
                    print(f"\tDuration:\t{returnjson["archive"]["duration"]}")
                    print(f"Files:\n{return_stderr}")

                    if json_data["SMTP"]["SendMailWhenSuccessful"]:
                        MailMessage = (
                            f"Backup was successful.\n"
                            f"\tArchive Name:\t{returnjson["archive"]["name"]}\n"
                            f"\tID:\t\t{returnjson["archive"]["id"]}\n"
                            f"\tStart:\t\t{returnjson["archive"]["start"]}\n"
                            f"\tEnd:\t\t{returnjson["archive"]["end"]}\n"
                            f"\tDuration:\t{returnjson["archive"]["duration"]}\n"
                            f"Files:\n{return_stderr}"
                        )

                        send_mail(
                            json_data["SMTP"],
                            Name,
                            MailMessage,
                            "Successful",
                        )
                case 1:
                    print("Backup was successful, but there were some warnings.")
                case 2:
                    print("The Backup wasn't successful, there were a fatal error.")

                    if json_data["SMTP"]["SendMailOnError"]:
                        send_mail(json_data["SMTP"], Name, return_stderr, "Error")
        else:
            print("The repo isn't currently initialized.")
            print("---------------------------------")
            proc = subprocess.run(
                [
                    "borg",
                    "init",
                    "--make-parent-dirs",
                    "--encryption=repokey",
                    f"{x["RemoteRepo"]}",
                ],
                capture_output=True,
            )
            output_init = proc.stderr.decode()

            print(output_init)
            print("---------------------------------")
            print(
                "The repo is now initialized. Please set the value 'Repo_Initialized' in the config to the value 'true'."
            )
    else:
        print(f"Backup '{Name}' is not active.")
