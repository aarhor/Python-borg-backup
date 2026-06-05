# BorgBackup with Python

**🥨🥨 DEUTSCHE VERSION [HIER](/README.md) 🥨🥨**

- [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [General](#general)
  - [Backup](#backup)
  - [SMTP](#smtp)
  - [Script Parameters](#script-parameters)
- [Monitoring](#monitoring)

---

This Python script allows backups to be created using [BorgBackup](https://www.borgbackup.org/) and stored on an external destination. Multiple backup sources and destinations can be defined through a JSON configuration file and are processed sequentially.

# Prerequisites

To use this script (including automated execution), the following software is required:

- [Python 3](https://www.python.org/downloads/)<br>
  _Tested with version 3.14.3_
- BorgBackup client and server installation.<br>

The following Python module is also required:

- `prettytable` => `pip install prettytable` or `sudo apt install python3-prettytable`<br>
  (Only imported and required when using the `--list` parameter)

# Usage

To use the script, create a copy of the example configuration file `config\config_example.json` and rename it to `config.json`.

It is also possible to store this file in a directory other than the `config` subdirectory.

> [!TIP]
> Although it is possible to specify a different path, it is recommended to keep the configuration file inside the `config` subdirectory.

Within the configuration file, some settings can reference other settings. These variables are unrelated to BorgBackup itself.

## General

| Setting                 | Documentation                                                                                                                                                | Available Variables | Recommended Setting              |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- | -------------------------------- |
| `Timestamp`             | [Python Datetime](https://docs.python.org/3.14/library/datetime.html#strftime-and-strptime-format-codes)                                                     | -                   | `%Y-%m-%d`                       |
| `LogFolder`             | -                                                                                                                                                            | -                   | `/var/lib/log/pythonBorgBackup/` |
| `LogLevel_Mail`         | Defines the log level used for email notifications                                                                                                           | -                   | `INFO`                           |
| `LogLevel_File`         | Defines the log level used for console output and file logging                                                                                               | -                   | `DEBUG`                          |
| `Allow Relocated Repos` | [Borg Documentation](https://borgbackup.readthedocs.io/en/stable/usage/general.html#environment-variables:~:text=BORG%5FRELOCATED%5FREPO%5FACCESS%5FIS%5FOK) | -                   | `no`                             |

This section contains general configuration options.

**`Timestamp`**<br>

The `Timestamp` setting is used to define the log file name. It can also be used as the archive name for backups.<br>
All formatting options supported by Python's `strftime()` function are supported. For optimal readability, however, `%Y-%m-%d` is recommended.

**`LogFolder`**<br>

A separate folder is created for each backup inside the directory specified by `LogFolder`. The log files are stored there using the naming pattern defined by `Timestamp`.

```plaintext
/var/lib/log/pythonBorgBackup
  |-> /Software 1
      |-> /2025-08-12.log
      |-> /2026-04-01.log
      |-> /2026-04-02.log
      |-> /2026-04-03.log
  |-> /Software 2
      |-> /2025-08-12.log
      |-> /2026-04-01.log
      |-> /2026-04-04.log
```

**`LogLevel_*`**<br>

- Default settings:
  - `"LogLevel_Mail": "INFO"`
  - `"LogLevel_File": "DEBUG"`
- Possible values:
  - `DEBUG`
  - `INFO`
  - `WARNING`
  - `ERROR`
  - `FATAL`

The `LogLevel_Mail` and `LogLevel_File` settings control the logging output.<br>
The order of severity is as follows:

`DEBUG` > `INFO` > `WARNING` > `ERROR` > `FATAL`

**`Allow Relocated Repos`**<br>

- Default setting:
  - `no`
- Possible values:
  - `yes`
  - `no`

If the destination repository has been moved, Borg will only continue after the prompt has been answered with either _yes_ or _no_. Since the script does not allow interactive input when running in automated mode, the response is predefined through this setting. If set to _yes_, execution continues and the new repository path will be accepted in future runs. This setting affects <ins>all</ins> configured backups.

> [!NOTE]
> If the value does not match the expected pattern (for example, the setting is left empty or contains an invalid value), Borg will treat it as _no_.

**Relevant log output:**

```plaintext
2026-04-05 17:13:14.809 DEBUG |  borg command: borg create --list --json --exclude /mnt/tools/backupdir1/Temp/Temp.log ssh://user@host:22/home/Backups/Test::{now:%Y-%m-%d} /mnt/tools/backupdir1
2026-04-05 17:13:16.306 ERROR |  The Backup wasn't successful, there were a fatal error.
2026-04-05 17:13:16.306 ERROR |  Warning: The repository at location ssh://user@host:22/home/Backups/Test was previously located at ssh://user@host:22/home/Backups/Test2
2026-04-05 17:13:16.306 ERROR |  Do you want to continue? [yN] no (from BORG_RELOCATED_REPO_ACCESS_IS_OK)
2026-04-05 17:13:16.306 ERROR |  Aborting.
2026-04-05 17:13:16.306 ERROR |  Repository access aborted
2026-04-05 17:13:16.306 INFO  |  Backup 'Software 1' done.
```

## Backup

| Setting              | Documentation                                                                                        | Available Variables | Recommended Setting |
| -------------------- | ---------------------------------------------------------------------------------------------------- | ------------------- | ------------------- |
| `Name`               | -                                                                                                    | -                   |                     |
| `SourcePath`         | -                                                                                                    | -                   |                     |
| `Exclude`            | -                                                                                                    | `{$SourcePathX}`    |                     |
| `RemoteRepo`         | [Borg Documentation](https://borgbackup.readthedocs.io/en/stable/usage/general.html#repository-urls) | -                   |                     |
| `ArchiveName`        | -                                                                                                    | `{now:$Timestamp}`  | `{now:$Timestamp}`  |
| `EncryptionPwd`      | -                                                                                                    | -                   |                     |
| `Repo_Initialized`   | -                                                                                                    | -                   |                     |
| `Pre_BackupCommand`  | -                                                                                                    | -                   |                     |
| `Post_BackupCommand` | -                                                                                                    | -                   |                     |
| `dry_run`            | -                                                                                                    | -                   |                     |
| `active`             | -                                                                                                    | -                   |                     |
| `Cleanup`            | [borg prune](https://borgbackup.readthedocs.io/en/stable/usage/prune.html)                           | -                   |                     |

> [!NOTE]
> For examples, refer to the [example configuration](config/config_example.json) file. It demonstrates how the various settings can be configured.

The `backup` section contains the backup jobs that should be created. Multiple source paths can be configured as individual backups and processed sequentially.

**`Name`**<br>

The name of the backup.<br>

**`SourcePath`**<br>

The source directory that should be backed up. As long as the directory is locally accessible, it can be backed up. If a network share should be backed up, it must be mounted beforehand.
After that, the directory can be backed up. Any source path supported by Borg can be used. Multiple paths can also be specified.

**`Exclude`**<br>

If certain directories or files should not be included in the backup, for example because they only contain temporary files or operating system files, they can be excluded using the `Exclude` setting.
Paths may be absolute or relative. Wildcards are also supported. For more information, see the [borg create documentation](https://borgbackup.readthedocs.io/en/stable/usage/create.html).
The variable `{$SourcePathX}` can be used to reference a source path when the directory or file to exclude is located within one of the configured source paths.

> [!NOTE]
> The _X_ in the variable `{$SourcePathX}` determines which path from `SourcePath` should be used. The index is zero-based.
> To use the first entry, replace X with `0` (`{$SourcePath0}`). To use the third entry, replace X with `2` (`{$SourcePath2}`).
> This syntax must also be used when only **one** source path is configured and the variable is used.

**`RemoteRepo`**<br>

The destination repository where Borg should store the backup data. Any repository type supported by [Borg](https://borgbackup.readthedocs.io/en/stable/usage/general.html#repository-urls) can be used.

> [!NOTE]
> Although Borg supports additional repository types, this script has only been successfully tested with SSH-based repositories (`ssh://user@host:port/path/to/repo`).

**`ArchiveName`**<br>

The name of the archive where the current data should be stored.

By default, the syntax from the `$Timestamp` variable is used. If `$Timestamp` is configured as `%Y-%m-%d`, the resulting archive name would be something like `2026-04-05`.

**`EncryptionPwd`**<br>

The password used to encrypt the archive.

> [!CAUTION]
>
> - Before initializing a repository, the script checks whether the password is empty or still matches one of the placeholder values from `config_example.json`. If this is the case, the script aborts with an error message.
> - In this case, update the password stored in `config.json`. It is recommended to use a local password manager such as [KeePass](https://keepass.info/index.html).
> - All files in the `config` directory (except `config_example.json`) are included in `.gitignore` by default.

**`Repo_Initialized`**<br>

- Default setting:
  - `false`
- Possible values:
  - `true`
  - `false`

This setting is currently used to determine whether the repository has already been initialized. Once the repository has been initialized successfully, the value **must** be changed from `false` to `true`.<br>
After initialization, an initial backup is created automatically. Depending on the total amount of data, this may take some time. Progress is not immediately visible in the output.

**`Pre_BackupCommand`**<br>

A command that should be executed **before** the actual backup starts. This can be used, for example, to stop a Docker container so that data cannot be modified while the backup is running.<br>
The individual command arguments must be separated by semicolons (`;`). => `docker;stop;Software`

**`Post_BackupCommand`**<br>

A command that should be executed **after** the backup has finished. Unless a general script failure occurs, this command will <ins>**always**</ins> be executed.<br>
The individual command arguments must be separated by semicolons (`;`). => `docker;start;Software`

**`dry_run`**<br>

- Default setting:
  - `false`
- Possible values:
  - `true`
  - `false`

Performs a test run <ins>without</ins> actually creating a backup. The final output will list all files that _would_ be affected.

**`active`**<br>

- Default setting:
  - `true`
- Possible values:
  - `true`
  - `false`

Specifies whether a backup is active (`true`) or inactive (`false`). An inactive backup generates a `Warning` message and is skipped.

**`Cleanup`**<br>

- Default setting:
  - `"daily": "14"`
  - `"monthly": "6"`
  - `"yearly": "1"`

After every successful backup, outdated archives are marked for deletion and permanently removed using [borg compact](https://borgbackup.readthedocs.io/en/stable/usage/compact.html).
For detailed information about the retention behavior of this setting, refer to the [borg prune examples](https://borgbackup.readthedocs.io/en/stable/usage/prune.html#examples).

## SMTP

| Setting              | Documentation                                                                   | Available Variables | Recommended Setting |
| -------------------- | ------------------------------------------------------------------------------- | ------------------- | ------------------- |
| `SendMailOn`         | -                                                                               | -                   |                     |
| `Login`              | -                                                                               | -                   |                     |
| `Password`           | -                                                                               | -                   |                     |
| `SMTP_Server`        | -                                                                               | -                   |                     |
| `Port`               | -                                                                               | -                   | `465`               |
| `DateHeaderTimezone` | [IANA Time Zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) | -                   | `Europe/Berlin`     |
| `Sender`             | -                                                                               | -                   |                     |
| `Recipient`          | -                                                                               | -                   |                     |

The `SMTP` section contains the settings required for sending completion emails, such as the destination SMTP server and its credentials.<br>

**`SendMailOn`**<br>

Controls under which circumstances an email should be sent. By default, an email is sent for all events with a severity level of _Warning_ or higher.<br>
The email contains the complete log output generated by the script. The exact content can be controlled through the `General` > `Logging` > `LogLevel_Mail` setting.

**`Login`**<br>

The username used to authenticate with the SMTP server. This may either be the primary email address or a separate username, depending on the provider.

**`Password`**<br>

The password used to authenticate with the SMTP server. In most cases, this will be an application-specific password or token, but some providers may still allow the use of the regular account password. This depends on the provider. If you are unsure, consult your provider's documentation or contact their support team.

**`SMTP_Server`**<br>

The SMTP server used to send email notifications.
Examples:

- Google: `smtp.gmail.com`
- Apple: `smtp.mail.me.com`
- Mailbox.org: `smtp.mailbox.org`
- posteo.de: `posteo.de`

**`Port`**<br>

The port that should be used for the SMTP connection. By default, port `465` is configured for TLS connections.<br>
If the connection must use STARTTLS, the standard port is `587`. Whenever possible, however, a direct TLS connection should be preferred for security reasons.

**`DateHeaderTimezone`**<br>

Specifies the time zone that should be used for the email's `Date` header. This ensures that the timestamp displayed in the completion email matches the desired time zone, regardless of the server's local system time zone.
If this setting is left empty, the script will use the server's local system time.

- Default setting: `Europe/Berlin`
- Possible values: Any valid [IANA time zone](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (for example `UTC`, `America/New_York`).

**`Sender`**<br>

The sender address used for outgoing emails. A display name can also be specified. `BorgBackup <mail1@example.com>`

**`Recipient`**<br>

The recipient address for notification emails. A display name can also be specified. `BorgBackup <mail1@example.com>`

## Script Parameters

**`--config_file="[Path to the config file]"`**<br>

The `--config_file=` parameter allows the script to be started using a configuration file located in a different directory.

**`--repo_init`**<br>

Initializes all repositories where `Repo_Initialized` is set to `False`. After the repository has been initialized successfully, `Repo_Initialized` must be changed to `True` manually.

> [!NOTE]
> No backup is created after a successful initialization when using this option.

**`--key_export`**<br>

Creates a backup of all repository keys and generates a text file in the `export` directory. The file can be printed and used later to restore the keys if necessary. Key import is currently not supported by the script and must be performed manually.<br>
The required Borg command is included in the generated file.

**`--single_import=[Backup Name]`**<br>

Runs only a single configured backup. Backup names containing spaces must be enclosed in quotation marks.

- `--single_import="Software 1"` <= Correct
- `--single_import=Software 1` <= Incorrect

**`--verify-data`**<br>

Verifies the integrity of all existing repository data before the backup starts.<br>

> [!CAUTION]
> Depending on the amount of data already stored in the repository, this process may take several hours to complete.

**`--skip_pre_check`**<br>

> [!NOTE]
> Only use this parameter when necessary and especially avoid using it in automated jobs, as repository issues may otherwise go undetected.

Skips the repository check that is normally performed before the backup starts.

**`--list`**<br>

Lists all configured backups.

```plaintext
+------------+--------+---------------------+-------+--------------+
| Name       | Active | Last Run            | Files | Size (Total) |
+------------+--------+---------------------+-------+--------------+
| Software 1 | True   | 2026-04-26 13:51:00 |     1 |    472.05 GB |
| Software 2 | True   | 2026-04-26 12:10:56 |     8 |    133.70 GB |
| Software 3 | True   | 2026-04-24 14:37:31 |     7 |      4.42 KB |
+------------+--------+---------------------+-------+--------------+
```

# Monitoring

The SMTP server and its credentials can be configured in the `SMTP` section of the configuration file.<br>
For monitoring tools, two JSON files are stored in the logging directory. Their contents are overwritten after every backup.

| File              | Content                                       |
| ----------------- | --------------------------------------------- |
| `stats.json`      | Information about the entire repository.      |
| `stats_last.json` | Information about the **most recent** backup. |

Once a backup has finished completely (regardless of whether it succeeded or failed), an email is sent containing the backup status.

Possible status values are:

- `🟩 Success`
- `🟧 Warning`
- `🟧 Skipped`
- `🟥 Error`
- `🟥 Fatal`

The status cell is color-coded according to the result.<br>
`🟧 Warning` and `🟧 Skipped` both belong to the "Warning" category. `🟥 Error` and `🟥 Fatal` both belong to the "Error" category.<br>

![Example](/nonscriptfiles/backupreport.png)

If the report is difficult to read in the email client (for example Thunderbird when using Dark Mode), a copy of the report is stored as an HTML file in the logging directory => `backup_report.html`

## TODO

Planned future improvements can be found [here](/nonscriptfiles/TODO.md).
