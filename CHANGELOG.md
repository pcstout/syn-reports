# Change Log

## Version 0.0.15 (2022-05-02)

### Added

- Additional args for benefactor-permissions report.

## Version 0.0.14 (2021-08-03)

### Added

- Added CSV column for "is_team_manager" to benefactor-permissions and entity-permissions reports.

## Version 0.0.13 (2021-08-02)

### Bug Fixes

- Fixed CSV writing on Windows.

## Version 0.0.12 (2021-07-19)

### Added

- Added system exit codes.

## Version 0.0.11 (2021-06-21)

### Added

- Added `--all` to entity_permissions_report to show all permissions.
- Do not set the `entity_parent_id` for projects in the benefactor_permissions_report CSV file.

## Version 0.0.10 (2020-11-04)

### Added

- Refactored caching.
- Added `company` field to `team-members` CSV file.

## Version 0.0.9 (2020-10-28)

### Added

- Added `entity_project_id` and `user_data` fields to benefactor-permissions CSV file.
- Removed `emails` field from benefactor-permissions CSV file.

## Version 0.0.8 (2020-10-14)

### Added

- Fix `--version` arg.

## Version 0.0.7 (2020-10-12)

### Added

- Updated benefactor-permissions report to work with projects and folders that have more than 20,000 child items.
- Added `--version` arg.

## Version 0.0.6 (2020-07-14)

### Added

- Added `entity_parent_id` to benefactor-permissions CSV file.

## Version 0.0.5 (2020-06-29)

### Added

- Upgraded synapseclient to version 2.1.0

## Version 0.0.4 (2020-06-17)

### Added

- Added benefactor-permissions report.

### Bug Fixes

- Extra blank line after every row in CSV files when run on Windows.

## Version 0.0.3 (2020-06-03)

### Added

- user-teams report: Ability to only report teams that have specific members.

## Version 0.0.2 (2020-06-02)

### Bug Fixes

- Log users and teams that the script user does not have permissions to.

## Version 0.0.1 (2020-02-26)

### Added

- Initial release.
