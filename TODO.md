# TODO

- [ ] **Monitoring**
  - [ ] Daten in ein Grafana Dasboard exportieren lassen
    - [ ] Gesamte Anzahl der Dateien
    - [ ] Gesamte Größe der Sicherung
    - [ ] Dauer der Sicherung
  - [ ] healthcheck.io Integration
- [ ] Zusammenfassung aller Backup-Ergebnisse (Erfolg/Fehler) in einer einzigen Tabelle am Ende der Mail.
- [ ] Global excludes
- [ ] **CLI-Erweiterung: `--check-updates` & `--install-updates` Parameter**
  - [ ] Nach neuen Updates vom borg Client suchen
  - [ ] Benachrichtigung in der Mail und im Log als WARNING
  - [ ] Mit `--install-updates` Neue Version installieren (benötigt `--check-updates`)

# Erledigt

- [ ] **Monitoring**
  - [x] json Ausgabe in stats.json speichern
- [x] Verschiedene Loglevel für Mail und Datei
- [x] Automatische Integritätsprüfung vor der Sicherung<br>
      => Abbrechen wenn ein Fehler festgestellt wurde
- [x] Automatisches Löschen alter Logdateien
- [x] Mehrere Quellpfade sichern
- [x] Vor und Nach der Sicherung einen Befehl ausführen
- [x] **CLI-Erweiterung: `--list` Parameter**
  - [x] json Daten über `borg info` erhalten und abspeichern
  - [x] Übersichtstabelle aller konfigurierten Backup-Jobs
  - [x] Anzeige von Status, letztem erfolgreichen Lauf und Repository-Größe
- [x] Einmal im Monat `borg check --verify-data` ausführen.