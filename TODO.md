# TODO

- [x] Automatisches Löschen alter Logdateien
- [x] Mehrere Quellpfade sichern
- [x] Vor und Nach der Sicherung einen Befehl ausführen
- [ ] Monitoring
  - [ ] Daten in ein Grafana Dasboard exportieren lassen
    - [ ] Gesamte Anzahl der Dateien
    - [ ] Gesamte Größe der Sicherung
    - [ ] Dauer der Sicherung
  - [ ] healthcheck.io Integration
  - [x] json Ausgabe in stats.json speichern
- [x] Verschiedene Loglevel für Mail und Datei
- [x] Automatische Integritätsprüfung vor der Sicherung<br>
      => Abbrechen wenn ein Fehler festgestellt wurde
- [ ] Zusammenfassung aller Backup-Ergebnisse (Erfolg/Fehler) in einer einzigen Tabelle am Ende der Mail.
- [ ] Einmal im Monat `borg check --verify-data` ausführen.
- [ ] Global excludes