# File History Duplicate Remover

A tool to clean up duplicate files in Windows File History backups by removing older copies while keeping the most recent version.

## Features

- Identifies duplicates based on filename patterns, file size, and SHA-256 checksum
- Keeps the newest version based on timestamp in filename
- Safe dry-run mode for testing
- Handles files with same base name and extension

## Installation

```bash
pipx install file-history-dups
```

## Usage

```bash
file-history-dups path/to/backup/folder [--dry-run]
```

Example output:
```
Deleted D:\Backups\file (2023_01_01 12_30_45 UTC).txt
Process completed. Total deleted: 2, Total skipped: 0
```

## How it works

1. Looks for files matching pattern: `name (YYYY_MM_DD HH_MM_SS UTC).ext`
2. Groups files by base name, extension, and file size
3. Verifies duplicates using SHA-256 checksum
4. Keeps newest file in each duplicate group
5. Deletes older copies (after confirmation in dry-run mode)

## Safety First

- Always test with `--dry-run` first
- Double-check your backups before running
- Files are permanently deleted (not moved to trash)

## More information

- [Structure of File History backups](https://superuser.com/a/1522178/11302)
- [File History keeps saving copies of files that haven't changed](https://superuser.com/q/997329/11302)
