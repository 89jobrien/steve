#!/usr/bin/env python3
"""Debug log rotation script for ~/.claude/debug directory.

Implements a retention policy:
- Keep: Files modified in the last 7 days
- Delete: Files older than 7 days

Usage:
    uv run debug_rotation.py [--dry-run] [--days N] [--verbose]
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_debug_dir() -> Path:
    """Get the debug directory path."""
    return Path.home() / ".claude" / "debug"


def get_file_age_days(file_path: Path) -> float:
    """Get the age of a file in days based on modification time."""
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    age = datetime.now() - mtime
    return age.total_seconds() / 86400


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable size."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def rotate_debug_logs(
    retention_days: int = 7,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict[str, int | str]:
    """Rotate debug logs based on retention policy.

    Args:
        retention_days: Number of days to retain logs
        dry_run: If True, only report what would be done
        verbose: If True, log each file operation

    Returns:
        Statistics about the rotation operation
    """
    debug_dir = get_debug_dir()

    if not debug_dir.exists():
        logger.warning(f"Debug directory does not exist: {debug_dir}")
        return {"error": "Debug directory not found"}

    stats = {
        "total_files": 0,
        "kept_files": 0,
        "deleted_files": 0,
        "kept_size": 0,
        "deleted_size": 0,
    }

    cutoff_date = datetime.now() - timedelta(days=retention_days)
    logger.info(f"Rotation cutoff: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Retention policy: {retention_days} days")

    if dry_run:
        logger.info("DRY RUN - No files will be deleted")

    # Process all .txt files in debug directory
    for file_path in debug_dir.glob("*.txt"):
        stats["total_files"] += 1
        file_size = file_path.stat().st_size
        age_days = get_file_age_days(file_path)

        if age_days > retention_days:
            # File is old, delete it
            stats["deleted_files"] += 1
            stats["deleted_size"] += file_size

            if verbose:
                logger.info(
                    f"DELETE: {file_path.name} "
                    f"(age: {age_days:.1f} days, size: {format_size(file_size)})"
                )

            if not dry_run:
                file_path.unlink()
        else:
            # File is recent, keep it
            stats["kept_files"] += 1
            stats["kept_size"] += file_size

            if verbose:
                logger.debug(
                    f"KEEP: {file_path.name} "
                    f"(age: {age_days:.1f} days, size: {format_size(file_size)})"
                )

    # Format sizes for output
    stats["kept_size_formatted"] = format_size(stats["kept_size"])
    stats["deleted_size_formatted"] = format_size(stats["deleted_size"])

    return stats


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rotate debug logs in ~/.claude/debug",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to retain logs (default: 7)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show details for each file",
    )

    args = parser.parse_args()

    logger.info("Starting debug log rotation...")

    stats = rotate_debug_logs(
        retention_days=args.days,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )

    if "error" in stats:
        logger.error(stats["error"])
        return 1

    # Print summary
    logger.info("=" * 50)
    logger.info("ROTATION SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total files scanned: {stats['total_files']}")
    logger.info(f"Files kept: {stats['kept_files']} ({stats['kept_size_formatted']})")
    logger.info(f"Files deleted: {stats['deleted_files']} ({stats['deleted_size_formatted']})")

    if args.dry_run:
        logger.info("(DRY RUN - no files were actually deleted)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
