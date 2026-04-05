# BorgBackup mit Python

**🦅🦅ENGLISH VERSION BELOW🦅🦅**

# Inhalt

- [Deutsch / German](#inhalt)
  - [Vorrausetzungen](#Vorrausetzungen)
  - [Nutzung](#nutzung)
    - [General](#general)
    - [backup](#backup)
    - [SMTP](#smtp)

Mit diesem Python Skript ist es möglich mittels [BorgBackup](https://www.borgbackup.org/) Backups anzustoßen und diese auf einem externen Ziel zu sichern.
Desweiteren ist es möglich über eine json Datei mehere Backup Quellen / Ziele anzugeben und diese nacheinaner sichern zu lassen.

## Vorrausetzungen

Damit das Skript (automatisiert) genutzt werden kann werden folgende Programme benötigt:

- [Python3](https://www.python.org/downloads/)<br>
  _Getestet mit 3.14.3_
- BorgBackup Client und Server Installation.<br>

## Nutzung

Damit das Skript genutzt werden kann, muss von der Beispiel config Datei `config\config_example.json` eine Kopie erstellt werden und diese `config.json` genannt werden.
Es ist auch möglich diese Datei in einen anderen Ordner als dem config Unterordner abzuspeichern.

> [!TIP]  
> Auch wenn es möglich ist einen anderen Pfad anzugeben, sollte die config Datei in dem config Unterordner belassen werden.

Innerhalb der config Datei ist es teilweise möglich auf andere Einstellungen zu verweisen. Diese Variablen haben mit BorgBackup nichts zu tun. Zur besseren

### General

| Einstellung | Beschreibung                                        | Doku                                                                                                     | Nutzbare Variablen | Empfohlene Einstellung |
| ----------- | --------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------ | ---------------------- |
| `Timestamp` | Zeitstemple für den Dateinamen der LogDatei.        | [python Datetime](https://docs.python.org/3.14/library/datetime.html#strftime-and-strptime-format-codes) | -                  | `%Y-%m-%d`             |
| `LogFolder` | Ordner wo die Logdateien gespeichert werden sollen. | -                                                                                                        | -                  |                        |
| `LogLevel`  | Das gewünschte Log Level.                           | -                                                                                                        | -                  | `INFO`                 |

In diesem Bereich lassen sich allgemeinere Einstellungen tätigen. Die Einstellung `Timestamp` wird genutzt um den Namen der Logdatei festzulegen. Des Weiteren ist es möglich `Timestamp` als Archivname für die Sicherung zu nutzen.<br>
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

`LogLevel` wird dafür genutzt um die Logging Ausgabe zu kontrollieren. Aktuell wird diese Einstellung auch für den Mailversand genutzt. Die Reihenfolge ist folgende: `DEBUG` > `INFO` > `WARNING` > `ERROR` > `FATAL`

### backup

| Einstellung        | Doku                                                                                        | Nutzbare Variablen | Empfohlene Einstellung |
| ------------------ | ------------------------------------------------------------------------------------------- | ------------------ | ---------------------- |
| `Name`             | -                                                                                           | -                  |                        |
| `SourcePath`       | -                                                                                           | -                  |                        |
| `Exclude`          | -                                                                                           | `{$SourcePath}`    |                        |
| `RemoteRepo`       | [borg Doku](https://borgbackup.readthedocs.io/en/stable/usage/general.html#repository-urls) | -                  |                        |
| `ArchiveName`      | -                                                                                           | `{now:$Timestamp}` | `{now:$Timestamp}`     |
| `EncryptionPwd`    | -                                                                                           | -                  |                        |
| `Repo_Initialized` | -                                                                                           | -                  |                        |
| `dry_run`          | -                                                                                           | -                  |                        |
| `active`           | -                                                                                           | -                  |                        |
| `Cleanup`          | [borg prune](https://borgbackup.readthedocs.io/en/stable/usage/prune.html)                  | -                  |                        |

> [!NOTE]
> Beispiele werden hier nicht direkt genannt. Schaue dir dafür die [Beispielconfig](config/config_example.json) Datei an. Dort werden einzelne Beispiele genannt.

Unter `backup` werden die gewünschten Sicherungen konfiguriert, die erstellt werden sollen. Es ist möglich mehrere Quellpfade als einzelene Backups anzugeben und diese sichern zu lassen.

**`Name`**<br>
Der Name der Sicherung.<br>

**`SourcePath`**<br>
Der Quellordner der gesichert werden soll. Solange der Ordner lokal verfügbar ist, kann dieser gesichert werden. Wenn eine Netzwerkfreigabe geischert werden soll, muss diese zuvor eingebunden werden.
Anschließend kann dieser Ordner gesichert werden. Als Quellpfad ist alles erlaubt was von borg unterstützt wird.

> [!WARNING]
> Es ist immer nur möglich, pro einzelne Sicherung, **ein** Ordner sichern zu lassen.

**`Exclude`**<br>
Sollten gewisse Ordner oder Dateien in der Sicherung nicht benötigt werden, da diese z.B. nur temporäre Dateien sind oder Systemdateien, können diese über die Einstellung `Exclude` ausgeschlossen werden.
Die Pfade können absolute oder auch relative Pfade sein. Wildcards werden auch unterstützt. Für weitere Informationen siehe die [borg create Dokumentation](https://borgbackup.readthedocs.io/en/stable/usage/create.html).
Es ist möglich, über die Variable `{$SourcePath}` den Quellpfad zu übernehmen sollten die Ordner / Dateien in einem Unterordner befinden.

**`RemoteRepo`**<br>
Das Ziel wo borg die Dateien hinsichern soll. Als Ziel kann alles genutzt werden was von [borg unterstützt wird](https://borgbackup.readthedocs.io/en/stable/usage/general.html#repository-urls).

> [!NOTE]
> Auch wenn andere Ziele von borg unterstützt werden sollten, wurde dieses Skript bisher nur mit ssh Zielen erfolgreich getestet (_ssh://user@host:port/path/to/repo_).

**`ArchiveName`**<br>
Der Name des Archives, wo die aktuellen Daten gespeichert werden sollen. Im Standard wird hier die Syntax von der `$Timestamp` Variable genommen. Das ist `%Y-%m-%d`. Daraus wird dann `2026-04-05` als Archivname.

**`EncryptionPwd`**<br>
Das Passwort was zur Verschlüsselung des Archives genutzt werden soll.

> [!CAUTION]
> Bei der Initialisierung des repos wird geprüft ob das angegebene Kennwort ein leeres oder eins der Beispielkennwörter aus der config Datei ist.
> Wenn dies der Fall ist, wird der weitere Vorgang abgebrochen.

**`Repo_Initialized`**<br>
Diese Einstellung wird, aktuell, genutzt um festzustellen ob das Repository bereits Initialisiert wurde. Sobald das repo erfolgreich Initialisiert wurde, **muss** der Wert von `false` auf `true` gesetzt werden.<br>
Nachdem das Repository eingerichtet wurde, erfolgt direkt im Anschluss eine erste Sicherung der Daten. Je nach Größe der gesamten Daten, kann dies einen Moment dauern. Dies ist in der Ausgabe nicht direkt ersichtlich.

**`dry_run`**<br>
Ein Durchlauf <ins>ohne</ins> dabei etwas wirklich zu sichern. In der Abschließenden Ausgabe werden einem alle Dateien aufgelistet die betroffen wären.

**`active`**<br>
Gibt an ob eine Sicherung aktiv ist (`true`) oder nicht (`false`). Eine nicht aktive Sicherung erzeugt ein `Warning` Fehler.

**`Cleanup`**<br>
Nach jeder erfolgreichen Sicherung werden im Zielarchiv veraltete Sicherungen als zu löschen markiert und mittels [borg compact](https://borgbackup.readthedocs.io/en/stable/usage/compact.html) gelöscht.
Im Standard werden folgende Sicherungen behalten:
- Täglich:    14 Tage
- Monatlich:   6 Monate
- Jährlich:    1 Jahr

Für ein genaues Verhalten dieser Einstellung, siehe die [borg Beispiel Dokumentation](https://borgbackup.readthedocs.io/en/stable/usage/prune.html#examples).

### SMTP

Im Bereich `SMTP` befinden sich die Einstellungen die für den Versand von den Abschlussmails benötigt werden. Wie z.B. der Ziel SMTP Server und dessen Zugangsdaten.<br>
