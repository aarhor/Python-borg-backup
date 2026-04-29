# Changelog

## 2026-04-29

### Added

- Updated automated `borg check` (see [borg documentation](https://borgbackup.readthedocs.io/en/stable/usage/check.html))
  - On every 1. of the month the scripts checks the repo data (like `--verify-data`)
  - Every second week the scripts checks the repositoy data. On the other week the scripts checks the archives.