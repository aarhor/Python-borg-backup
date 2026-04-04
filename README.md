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
> Auch wenn es möglich ist einen anderen Pfad anzugeben, empfehle ich die config Datei in dem config Unterordner zu belassen.

Innerhalb der config Datei ist es teilweise möglich auf andere Einstellungen zu verweisen. Diese Variablen haben mit BorgBackup nichts zu tun. Zur besseren
### General

| Einstellung | Beschreibung                                                       | Doku                                                                                                     | Nutzbare Variablen | Empfohlene Einstellung |
| ----------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------- | ------------------ | ---------------------- |
| `Timestamp` | Zeitstemple für den Dateinamen der LogDatei.                       | [python Datetime](https://docs.python.org/3.14/library/datetime.html#strftime-and-strptime-format-codes) | -                  | `%Y-%m-%d`             |
| `LogFolder` | Ordner wo die Logdateien gespeichert werden sollen.                | -                                                                                                        | -                  |                        |
| `LogLevel`  | Das gewünschte Log Level.<br>=>`DEBUG`, `INFO`, `WARNING`, `ERROR` | -                                                                                                        | -                  | `INFO`                 |

In diesem Bereich lassen sich allgemeinere Einstellungen tätigen. Die Einstellung `Timestamp` wird genutzt um den Namen der Logdatei festzulegen. Des Weiteren ist es möglich `Timestamp` als Archivname für die Sicherung zu nutzen.<br>
Unter `LogFolder` wird pro backup ein Ordner angelegt, innerhalb dieses Ordners werden die Logdateien nach dem Muster von `Timestamp` gespeichert.
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

`LogLevel` wird dafür genutzt um die Logging Ausgabe zu kontrollieren. Aktuell wird diese Einstellung auch für den Mailversand genutzt.
### backup

Unter `backup` werden die gewünschten Sicherungen konfiguriert, die erstellt werden sollen. Es ist möglich mehrere Quellpfade als einzelene Backups anzugeben und diese sichern zu lassen.

> [!WARNING]  
> Es ist immer möglich immer nur **ein** Ordner, pro einzelne Sicherung, sichern zu lassen.

Sollten gewisse Ordner oder Dateien in der Sicherung nicht benötigt werden, da diese z.B. nur temporäre Dateien sind oder Systemdateien, können diese über die Einstellung `Exclude` ausgeschlossen werden.
Die angegebenen Pfade **müssen** absolute Pfade sein. Es ist jedoch möglich, über die Variable `{$SourcePath}` den Quellpfad zu übernehmen sollten die Ordner / Dateien in einem Unterordner befinden.

### SMTP

Im Bereich `SMTP` befinden sich die Einstellungen die für den Versand von den Abschlussmails benötigt werden. Wie z.B. der Ziel SMTP Server und dessen Zugangsdaten.<br>
