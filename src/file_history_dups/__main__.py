import os
import re
import argparse
import hashlib
from datetime import datetime
from collections import defaultdict

FILENAME_PATTERN = re.compile(
    r"^(.+?) \((\d{4}_\d{2}_\d{2} \d{2}_\d{2}_\d{2} UTC)\)\.(.+?)$"
)


def parse_filename(filename):
    match = FILENAME_PATTERN.match(filename)
    if not match:
        return None
    base, timestamp_str, ext = match.groups()
    try:
        timestamp = datetime.strptime(timestamp_str, "%Y_%m_%d %H_%M_%S UTC")
    except ValueError:
        return None
    return {"base": base, "timestamp": timestamp, "ext": ext, "original": filename}


def compute_checksum(filepath, block_size=65536):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            block = f.read(block_size)
            while block:
                hasher.update(block)
                block = f.read(block_size)
    except OSError as e:
        return None, str(e)
    return hasher.hexdigest(), None


def process_directory(dirpath, filenames, dry_run=False):
    groups = defaultdict(list)
    for filename in filenames:
        parsed = parse_filename(filename)
        if not parsed:
            continue
        full_path = os.path.join(dirpath, filename)
        try:
            file_size = os.path.getsize(full_path)
        except OSError as e:
            print(f"Error accessing {full_path}: {e}")
            continue
            
        groups[(parsed["base"], parsed["ext"], file_size)].append(
            {"path": full_path, "timestamp": parsed["timestamp"], "original": filename}
        )

    total_deleted = 0
    total_skipped = 0

    for (base, ext, _), group in groups.items():
        if len(group) < 2:
            continue

        checksums = []
        errors = []
        for file_info in group:
            checksum, error = compute_checksum(file_info["path"])
            if error:
                errors.append((file_info["path"], error))
            checksums.append(checksum)

        if errors:
            for path, error in errors:
                print(f"Error reading {path}: {error}")
            total_skipped += len(group) - 1
            continue

        # Group files by their checksum
        checksum_groups = defaultdict(list)
        for file_info, checksum in zip(group, checksums):
            checksum_groups[checksum].append(file_info)

        # Process each checksum subgroup
        for subgroup in checksum_groups.values():
            if len(subgroup) < 2:
                continue
                
            sorted_subgroup = sorted(subgroup, key=lambda x: x["timestamp"], reverse=True)
            to_delete = sorted_subgroup[1:]
            
            for file_info in to_delete:
                if dry_run:
                    print(f"Dry run: Would delete {file_info['path']}")
                    total_deleted += 1
                else:
                    try:
                        os.remove(file_info["path"])
                        print(f"Deleted {file_info['path']}")
                        total_deleted += 1
                    except OSError as e:
                        print(f"Error deleting {file_info['path']}: {e}")
                        total_skipped += 1

    return total_deleted, total_skipped


def main():
    parser = argparse.ArgumentParser(
        description="Remove duplicate files with timestamp in filenames."
    )
    parser.add_argument("directory", help="Directory to process for duplicate files")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate deletion without modifying filesystem",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        return

    total_deleted = 0
    total_skipped = 0

    for dirpath, _, filenames in os.walk(args.directory):
        deleted, skipped = process_directory(dirpath, filenames, args.dry_run)
        total_deleted += deleted
        total_skipped += skipped

    print(
        f"Process completed. Total deleted: {total_deleted}, Total skipped: {total_skipped}"
    )


if __name__ == "__main__":
    main()
