# BorgBackup mit Python

**🦅🦅ENGLISH VERSION BELOW🦅🦅**

- [Deutsch / German](#deutsch--german)
  - [Voraussetzungen](#voraussetzungen)
  - [Nutzung](#nutzung)
    - [General](#general)
    - [backup](#backup)
    - [SMTP](#smtp)
    - [Skript Parameter](#skript-parameter)
  - [Monitoring](#monitoring)
- [English / Englisch](#english--englisch)

# Deutsch / German

Mit diesem Python-Skript können Backups mittels [BorgBackup](https://www.borgbackup.org/) angestoßen und auf einem externen Ziel gesichert werden. Über eine JSON-Konfigurationsdatei lassen sich mehrere Backup-Quellen und -Ziele definieren, die sequenziell abgearbeitet werden.

## Voraussetzungen

Damit das Skript (automatisiert) genutzt werden kann werden, folgende Programme benötigt:

- [Python3](https://www.python.org/downloads/)<br>
  _Getestet mit 3.14.3_
- BorgBackup Client und Server Installation.<br>

Des Weiteren werden folgende Python-Module benötigt:

- `prettytable` => `pip install prettytable` or `sudo apt install python3-prettytable`

## Nutzung

Damit das Skript genutzt werden kann, muss von der Beispiel-Konfigurationsdatei `config\config_example.json` eine Kopie erstellt werden und diese `config.json` genannt werden.
Es ist auch möglich diese Datei in einen anderen Ordner als dem Config-Unterordner abzuspeichern.

> [!TIP]  
> Auch wenn es möglich ist einen anderen Pfad anzugeben, sollte die config Datei in dem Config-Unterordner belassen werden.

Innerhalb der config Datei ist es teilweise möglich auf andere Einstellungen zu verweisen. Diese Variablen haben mit BorgBackup nichts zu tun.

### General

| Einstellung             | Doku                                                                                                                                                | Nutzbare Variablen | Empfohlene Einstellung           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | -------------------------------- |
| `Timestamp`             | [python Datetime](https://docs.python.org/3.14/library/datetime.html#strftime-and-strptime-format-codes)                                            | -                  | `%Y-%m-%d`                       |
| `LogFolder`             | -                                                                                                                                                   | -                  | `/var/lib/log/pythonBorgBackup/` |
| `LogLevel_Mail`         | Bestimmt das LogLevel für den Mailversand                                                                                                           | -                  | `INFO`                           |
| `LogLevel_File`         | Bestimmt das LogLevel für den Ausgabe in der Konsole und Logging in eine Datei.                                                                     | -                  | `DEBUG`                          |
| `Allow Relocated Repos` | [Borg Doku](https://borgbackup.readthedocs.io/en/stable/usage/general.html#environment-variables:~:text=BORG%5FRELOCATED%5FREPO%5FACCESS%5FIS%5FOK) | -                  | `no`                             |

In diesem Bereich lassen sich allgemeinere Einstellungen vornehmen.

**`Timestamp`**<br>

Die Einstellung `Timestamp` wird genutzt um den Namen der Logdatei festzulegen. Des Weiteren ist es möglich `Timestamp` als Archivname für die Sicherung zu nutzen.<br>
Es werden alle [formatierungen der python Funktion `strftime()`](https://docs.python.org/3.14/library/datetime.html#strftime-and-strptime-format-codes) unterstützt. Für eine Optimale Übersicht wird jedoch `%Y-%m-%d` empfohlen.

**`LogFolder`**<br>

Unter `LogFolder` wird pro Sicherung ein Ordner angelegt, innerhalb dieses Ordners werden die Logdateien nach dem Muster von `Timestamp` gespeichert.

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

- Standardeinstellung:
  - `"LogLevel_Mail": "INFO"`
  - `"LogLevel_File": "DEBUG"`
- Mögliche Werte:
  - `DEBUG`
  - `INFO`
  - `WARNING`
  - `ERROR`
  - `FATAL`

Mit den Einstellungen `LogLevel_Mail` & `LogLevel_File` wird die Logging Ausgabe kontrolliert.<br>
Die Reihenfolge ist folgende: `DEBUG` > `INFO` > `WARNING` > `ERROR` > `FATAL`

**`Allow Relocated Repos`**<br>

- Standardeinstellung:
  - `no`
- Mögliche Werte:
  - `yes`
  - `no`

Wenn das Ziel Repository verschoben wurde, fährt borg erst mit der Sicherung fort, wenn die Abfrage mit _yes_ oder _no_ beantwortet wurde. Da das Skript im Automatikmodus keine interaktiven Eingaben erlaubt, wird die Antwort über diese Einstellung vorab festgelegt. Bei _yes_ wird die Ausführung fortgeführt und der neue Pfad wird zukünftig akzeptiert. Diese Einstellung betrifft <ins>alle</ins> konfigurierten Sicherungen.

> [!NOTE]
> Wenn die Eingabe nicht dem vorgegebene Muster entspricht (Einstellung bleibt leer oder es steht was komplett anderes drin), wird borg seitig _no_ angegeben.

**Relevante LOG Ausgabe**:

```plaintext
2026-04-05 17:13:14.809	DEBUG	|  borg command: borg create --list --json --exclude /mnt/tools/backupdir1/Temp/Temp.log ssh://user@host:22/home/Backups/Test::{now:%Y-%m-%d} /mnt/tools/backupdir1
2026-04-05 17:13:16.306	ERROR	|  The Backup wasn't successful, there were a fatal error.
2026-04-05 17:13:16.306	ERROR	|  	Warning: The repository at location ssh://user@host:22/home/Backups/Test was previously located at ssh://user@host:22/home/Backups/Test2
2026-04-05 17:13:16.306	ERROR	|  	Do you want to continue? [yN] no (from BORG_RELOCATED_REPO_ACCESS_IS_OK)
2026-04-05 17:13:16.306	ERROR	|  	Aborting.
2026-04-05 17:13:16.306	ERROR	|  	Repository access aborted
2026-04-05 17:13:16.306	INFO	|  Backup 'Software 1' done.
```

### backup

| Einstellung          | Doku                                                                                        | Nutzbare Variablen | Empfohlene Einstellung |
| -------------------- | ------------------------------------------------------------------------------------------- | ------------------ | ---------------------- |
| `Name`               | -                                                                                           | -                  |                        |
| `SourcePath`         | -                                                                                           | -                  |                        |
| `Exclude`            | -                                                                                           | `{$SourcePathX}`   |                        |
| `RemoteRepo`         | [Borg Doku](https://borgbackup.readthedocs.io/en/stable/usage/general.html#repository-urls) | -                  |                        |
| `ArchiveName`        | -                                                                                           | `{now:$Timestamp}` | `{now:$Timestamp}`     |
| `EncryptionPwd`      | -                                                                                           | -                  |                        |
| `Repo_Initialized`   | -                                                                                           | -                  |                        |
| `Pre_BackupCommand`  | -                                                                                           | -                  |                        |
| `Post_BackupCommand` | -                                                                                           | -                  |                        |
| `dry_run`            | -                                                                                           | -                  |                        |
| `active`             | -                                                                                           | -                  |                        |
| `Cleanup`            | [borg prune](https://borgbackup.readthedocs.io/en/stable/usage/prune.html)                  | -                  |                        |

> [!NOTE]
> Für Beispiele schaue dir dafür die [Beispielconfig](config/config_example.json) Datei an. Dort wird gezeigt wie sich was Konfigurieren lässt.

Unter `backup` werden die gewünschten Sicherungen konfiguriert, die erstellt werden sollen. Es ist möglich mehrere Quellpfade als einzelene Backups anzugeben und diese sichern zu lassen.

**`Name`**<br>

Der Name der Sicherung.<br>

**`SourcePath`**<br>

Der Quellordner der gesichert werden soll. Solange der Ordner lokal verfügbar ist, kann dieser gesichert werden. Wenn eine Netzwerkfreigabe geischert werden soll, muss diese zuvor eingebunden werden.
Anschließend kann dieser Ordner gesichert werden. Als Quellpfad ist alles erlaubt was von borg unterstützt wird. Es ist möglich mehrere Pfade zu sichern.

**`Exclude`**<br>

Sollten gewisse Ordner oder Dateien in der Sicherung nicht benötigt werden, da diese z.B. nur temporäre Dateien sind oder Systemdateien, können diese über die Einstellung `Exclude` ausgeschlossen werden.
Die Pfade können absolute oder auch relative Pfade sein. Wildcards werden auch unterstützt. Für weitere Informationen siehe die [borg create Dokumentation](https://borgbackup.readthedocs.io/en/stable/usage/create.html).
Es ist möglich, über die Variable `{$SourcePathX}` den Quellpfad zu übernehmen sollten sich die Ordner / Dateien in einem Unterordner befinden.

> [!NOTE]
> Über das _X_ in der Variable `{$SourcePathX}` lässt sich steuern welcher Pfad aus `SourcePath` genutzt werden soll. Die Angabe ist 0-basiert.
> Wenn nun der 1. Eintrag genutzt werden soll, so muss das X mit einer "0" getauscht werden (`{$SourcePath0}`). Bei dem 3. Eintrag ist es dann "2" (`{$SourcePath2}`).
> Diese Schreibweise muss auch dann genutzt werden, vorausgesetzt die Variable wird genutzt, wenn unter `SourcePath` nur **ein** Pfad angegeben ist.

**`RemoteRepo`**<br>

Das Ziel wo borg die Dateien hinsichern soll. Als Ziel kann alles genutzt werden was von [borg unterstützt wird](https://borgbackup.readthedocs.io/en/stable/usage/general.html#repository-urls).

> [!NOTE]
> Auch wenn andere Ziele von borg unterstützt werden sollten, wurde dieses Skript bisher nur mit ssh Zielen erfolgreich getestet (_ssh://user@host:port/path/to/repo_).

**`ArchiveName`**<br>

Der Name des Archives, wo die aktuellen Daten gespeichert werden sollen. Im Standard wird hier die Syntax von der `$Timestamp` Variable genommen. Das ist `%Y-%m-%d`. Daraus wird dann `2026-04-05` als Archivname.

**`EncryptionPwd`**<br>

Das Passwort was zur Verschlüsselung des Archives genutzt werden soll.

> [!CAUTION]
>
> - Das Skript prüft vor der Initialisierung, ob das Kennwort leer ist oder einem der Platzhalter aus der config_example.json entspricht. In diesem Fall bricht das Skript mit einer Fehlermeldung ab. Ändere in diesem Fall in der `config.json` das hinterlegte Kennwort. Nutze hierfür z.B. einen lokalen Passwort Manager wie [KeePass](https://keepass.info/index.html).
> - Alle Dateien (außer die Datei `config_example.json`) aus dem Ordner `config` sind standardmäßig in der .gitignore hinterlegt.

**`Repo_Initialized`**<br>

- Standardeinstellung:
  - `false`
- Mögliche Werte:
  - `true`
  - `false`

Diese Einstellung wird, aktuell, genutzt um festzustellen ob das Repository bereits Initialisiert wurde. Sobald das repo erfolgreich Initialisiert wurde, **muss** der Wert von `false` auf `true` gesetzt werden.<br>
Nachdem das Repository eingerichtet wurde, erfolgt direkt im Anschluss eine erste Sicherung der Daten. Je nach Größe der gesamten Daten, kann dies einen Moment dauern. Dies ist in der Ausgabe nicht direkt ersichtlich.

**`Pre_BackupCommand`**<br>

Ein Befehl der **vor** der eigentlichen Sicherung ausgeführt werden soll. Hierdurch kann z.B. ein Docker Container beendet werden damit die Daten während der Sicherung nicht verändert werden können.<br>
Die einzelnen Teile des Befehls müssen mit einem Semikolon ";" getrennt werden. => `docker;stop;Software`

**`Post_BackupCommand`**<br>

Ein Befehl der **nach** der eigentlichen Sicherung ausgeführt werden soll. Sollte es nicht zu einem allgemeinen Fehler kommen wird dieser Befehl <ins>**immer**</ins> ausgeführt.<br>
Die einzelnen Teile des Befehls müssen mit einem Semikolon ";" getrennt werden. => `docker;start;Software`

**`dry_run`**<br>

- Standardeinstellung:
  - `false`
- Mögliche Werte:
  - `true`
  - `false`

Ein Durchlauf <ins>ohne</ins> dabei etwas wirklich zu sichern. In der Abschließenden Ausgabe werden einem alle Dateien aufgelistet die betroffen wären.

**`active`**<br>

- Standardeinstellung:
  - `true`
- Mögliche Werte:
  - `true`
  - `false`

Gibt an ob eine Sicherung aktiv ist (`true`) oder nicht (`false`). Eine nicht aktive Sicherung erzeugt einen `Warning` Fehler und wird nicht weiter beachtet.

**`Cleanup`**<br>

- Standardeinstellung:
  - `"daily": "14"`
  - `"monthly": "6"`
  - `"yearly": "1"`

Nach jeder erfolgreichen Sicherung werden im Zielarchiv veraltete Sicherungen als zu löschen markiert und mittels [borg compact](https://borgbackup.readthedocs.io/en/stable/usage/compact.html) gelöscht.
Für ein genaues Verhalten dieser Einstellung, siehe die [borg Beispiel Dokumentation](https://borgbackup.readthedocs.io/en/stable/usage/prune.html#examples).

### SMTP

| Einstellung          | Doku                                                                           | Nutzbare Variablen | Empfohlene Einstellung |
| -------------------- | ------------------------------------------------------------------------------ | ------------------ | ---------------------- |
| `SendMailOn`         | -                                                                              | -                  |                        |
| `Login`              | -                                                                              | -                  |                        |
| `Password`           | -                                                                              | -                  |                        |
| `SMTP_Server`        | -                                                                              | -                  |                        |
| `Port`               | -                                                                              | -                  | 465                    |
| `DateHeaderTimezone` | [IANA-Zeitzonen](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) | -                  | `Europe/Berlin`        |
| `Sender`             | -                                                                              | -                  |                        |
| `Recipient`          | -                                                                              | -                  |                        |

Im Bereich `SMTP` befinden sich die Einstellungen die für den Versand von den Abschlussmails benötigt werden. Wie z.B. der Ziel SMTP Server und dessen Zugangsdaten.<br>

**`SendMailOn`**<br>

Steuert in welchem Fall eine Mail gesendet werden soll. In der Standardeinstellung wird ab der Stufe _Warning_ eine Mail verschickt.<br>
Der Inhalt der Mail umfasst den gesamten Inhalt des Skript eigenen Loggings. Der genaue Inhalt lässt sich über die Einstellung `General` > `Logging` > `LogLevel_Mail` konfigurieren.

**`Login`**<br>

Der Anmeldename an dem SMTP Server. Dies kann die eigene Haupt E-Mail Adresse sein oder der normale Benutzername.

**`Password`**<br>

Das Passwort was für die Anmeldung am SMTP Server benötigt wird. In der Regel ist dies ein eigener App-Token, kann aber auch das normale Benutzerkennwort sein. Dies ist je nach Anbieter unterschiedlich. Bei Unsicherheiten frage beim Support des Anbieters nach.

**`SMTP_Server`**<br>

Der SMTP Server für den weiteren Mailversand.
Beispiele:

- Google: `smtp.gmail.com`
- Apple: `smtp.mail.me.com`
- Mailbox.org: `smtp.mailbox.org`
- posteo.de: `posteo.de`

**`Port`**<br>

Der gewünschte Port. Standardmäßig ist hier 465 für TLS eingestellt.<br>
Muss die Verbindung über STARTTLS erfolgen, ist hier der Standardport 587. Nach Möglichkeit sollte jedoch **immer**, aus Sicherheitsgründen, eine Verbindung über TLS aufgebaut werden.

**`DateHeaderTimezone`**<br>

Gibt die Zeitzone an, die im Header der E-Mail für das Datum verwendet werden soll. Dies stellt sicher, dass die Sendezeit in der Abschlussmail korrekt angezeigt wird, unabhängig davon, in welcher Zeitzone der Server selbst läuft.
Wird dieses Feld leer gelassen, nutzt das Skript die lokale Systemzeit des Servers.

- Standardeinstellung: `Europe/Berlin`
- Mögliche Werte: Alle gültigen [IANA-Zeitzonen](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) (z. B. `UTC`, `America/New_York`).

**`Sender`**<br>

Der Absender der Mail. Es ist auch möglich einen Namen mitzugeben. `BorgBackup <mail1@example.com>`

**`Recipient`**<br>

Der Empfänger der Mail. Es ist auch möglich einen Namen mitzugeben. `BorgBackup <mail1@example.com>`

### Skript Parameter

**`--config_file="[Pfad zur config Datei]"`**<br>

Über den Parameter `--config_file=` ist es möglich die config Datei aus einem anderen Verzeichnis zu starten.

**`--repo_init`**<br>

Initiiert alle repos wo die Einstellung `Repo_Initialized` auf `False` gestellt ist. Nach der Einrichtung muss `Repo_Initialized` auf `True` umgestellt werden!

> [!NOTE]
> Mit dieser Einstellung wird nach der Erfolgreichen Initiierung keine Sicherung angelegt.

**`--key_export`**<br>

Erstellt eine Sicherung aller Schlüssel und erstellt im Ordner `export` eine Textdatei die ausgedruckt werden kann und bei Bedarf wieder importiert werden kann. Ein Import wird aktuell nicht unterstützt und muss manuell erfolgen.<br>
Der benötigte Befehl ist in der Datei hinterlegt.

**`--single_import=[Name der Sicherung]`**<br>

Startet nur eine einzelne Sicherung. Sicherungen mit Leerzeichen im Namen müssen mit " umschlossen werden.

- `--single_import="Software 1"` <= Knorke
- `--single_import=Software 1`   <= Nicht so Knorke

**`--verify-data`**<br>

Prüft vor der eigentlichen Sicherung auch alle vorhandene Dateien auf Integrität.<br>

> [!CAUTION]
> Je nach Größe der bereits vorhandenen Dateien, kann die Sicherung hiermit auch mehere Stunden dauern!

**`--skip_pre_check`**<br>

> [!NOTE]
> Setze diesen Parameter nur bei Bedarf und insbesondere nicht automatisiert im Hintergrund, da dardurch eventuelle Fehler im repo nicht erkannt werden können.

Überspringt den check der vor der Sicherung durchgeführt wird.

**`--list`**<br>

Listet alle konfigurierten Sicherungen auf.

```plaintext
+------------+--------+---------------------+-------+--------------+
| Name       | Active | Last Run            | Files | Size (Total) |
+------------+--------+---------------------+-------+--------------+
| Software 1 | True   | 2026-04-26 13:51:00 |     1 |    472.05 GB |
| Software 2 | True   | 2026-04-26 12:10:56 |     8 |    133.70 GB |
| Software 3 | True   | 2026-04-24 14:37:31 |     7 |      4.42 KB |
+------------+--------+---------------------+-------+--------------+
```

## Monitoring

Nach jedem Durchlauf wird eine Mail mit den aktuellen Logausgaben versendet. In der config Datei kann der SMTP Server unter `SMTP` eingerichtet werden.<br>
Für Monitoring tools werden in dem Logging verzeichnis zwei json Dateien gespeichert. Der Inhalt wird nach jeder Sicherung überschrieben.

| Datei             | Inhalt                                       |
| ----------------- | -------------------------------------------- |
| `stats.json`      | Informationen über das komplette repo.       |
| `stats_last.json` | Informationen über die **letzte** Sicherung. |

### TODO

Die noch geplanten Anpassungen finden sich [hier](TODO.md).

---

# English / Englisch

Later please be patient.
