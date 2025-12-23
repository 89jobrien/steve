#!/usr/bin/env python3
"""History.jsonl archival script for ~/.claude directory.

Implements monthly archival:
- Keep: Entries from the last 30 days in history.jsonl
- Archive: Older entries to compressed monthly files

Archives are stored in ~/.claude/archive/history/

Usage:
    uv run history_archival.py [--dry-run] [--days N] [--verbose]
"""

import argparse
import gzip
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_claude_dir() -> Path:
    return Path.home() / ".claude"


def get_history_file() -> Path:
    return get_claude_dir() / "history.jsonl"


def get_archive_dir() -> Path:
    return get_claude_dir() / "archive" / "history"


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def parse_timestamp(entry: dict) -> datetime | None:
    ts = entry.get("timestamp")
    if ts is None:
        return None
    if ts > 1e12:
        ts = ts / 1000
    try:
        return datetime.fromtimestamp(ts)
    except (ValueError, OSError):
        return None


def process_entry(
    line: str,
    cutoff_date: datetime,
    recent: list[str],
    archives: dict[str, list[str]],
    stats: dict,
    verbose: bool,
) -> None:
    """Process a single history entry."""
    stats["total_entries"] += 1

    try:
        entry = json.loads(line)
    except json.JSONDecodeError:
        recent.append(line)
        stats["kept_entries"] += 1
        stats["parse_errors"] += 1
        return

    entry_date = parse_timestamp(entry)

    if entry_date is None:
        recent.append(line)
        stats["kept_entries"] += 1
        stats["parse_errors"] += 1
        return

    if entry_date >= cutoff_date:
        recent.append(line)
        stats["kept_entries"] += 1
        return

    month_key = entry_date.strftime("%Y-%m")
    archives[month_key].append(line)
    stats["archived_entries"] += 1

    if verbose:
        logger.debug(f"ARCHIVE: Entry from {entry_date.strftime('%Y-%m-%d')} -> {month_key}")


def write_archives(
    archive_dir: Path,
    archive_entries: dict[str, list[str]],
    dry_run: bool,
    verbose: bool,
) -> list[str]:
    """Write archive files and return list of created archives."""
    if not archive_entries:
        return []

    if not dry_run:
        archive_dir.mkdir(parents=True, exist_ok=True)

    archives_created = []
    for month_key, entries in sorted(archive_entries.items()):
        archive_file = archive_dir / f"history-{month_key}.jsonl.gz"

        if verbose:
            logger.info(f"Creating archive: {archive_file.name} ({len(entries)} entries)")

        if not dry_run:
            mode = "ab" if archive_file.exists() else "wb"
            with gzip.open(archive_file, mode) as f:
                content = "\n".join(entries) + "\n"
                f.write(content.encode("utf-8"))

        archives_created.append(f"{month_key} ({len(entries)} entries)")

    return archives_created


def archive_history(
    retention_days: int = 30,
    dry_run: bool = False,
    verbose: bool = False,
) -> dict:
    """Archive old history entries to monthly compressed files."""
    history_file = get_history_file()
    archive_dir = get_archive_dir()

    if not history_file.exists():
        logger.warning(f"History file does not exist: {history_file}")
        return {"error": "History file not found"}

    original_size = history_file.stat().st_size
    cutoff_date = datetime.now() - timedelta(days=retention_days)

    logger.info(f"Archival cutoff: {cutoff_date.strftime('%Y-%m-%d')}")
    logger.info(f"Retention policy: {retention_days} days in main file")

    if dry_run:
        logger.info("DRY RUN - No files will be modified")

    recent_entries: list[str] = []
    archive_entries: dict[str, list[str]] = defaultdict(list)
    stats = {
        "total_entries": 0,
        "kept_entries": 0,
        "archived_entries": 0,
        "original_size": original_size,
        "parse_errors": 0,
    }

    with history_file.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            process_entry(line, cutoff_date, recent_entries, archive_entries, stats, verbose)

    archives_created = write_archives(archive_dir, archive_entries, dry_run, verbose)

    if not dry_run:
        with history_file.open("w") as f:
            for entry in recent_entries:
                f.write(entry + "\n")

    new_size = sum(len(e) + 1 for e in recent_entries) if recent_entries else 0
    stats["new_size"] = new_size
    stats["original_size_formatted"] = format_size(original_size)
    stats["new_size_formatted"] = format_size(new_size)
    stats["space_saved"] = original_size - new_size
    stats["space_saved_formatted"] = format_size(max(0, original_size - new_size))
    stats["archives_created"] = archives_created

    return stats


def print_summary(stats: dict, dry_run: bool) -> None:
    """Print archival summary."""
    logger.info("=" * 50)
    logger.info("ARCHIVAL SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Total entries processed: {stats['total_entries']}")
    logger.info(f"Entries kept in history.jsonl: {stats['kept_entries']}")
    logger.info(f"Entries archived: {stats['archived_entries']}")
    logger.info(f"Original size: {stats['original_size_formatted']}")
    logger.info(f"New size: {stats['new_size_formatted']}")
    logger.info(f"Space saved: {stats['space_saved_formatted']}")

    if stats.get("parse_errors", 0) > 0:
        logger.warning(f"Entries with parse errors (kept): {stats['parse_errors']}")

    if stats.get("archives_created"):
        logger.info("Archives created/updated:")
        for archive in stats["archives_created"]:
            logger.info(f"  - {archive}")

    if dry_run:
        logger.info("(DRY RUN - no files were actually modified)")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Archive old history entries from ~/.claude/history.jsonl",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--days", type=int, default=30, help="Days to retain (default: 30)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show details")

    args = parser.parse_args()

    logger.info("Starting history archival...")
    stats = archive_history(retention_days=args.days, dry_run=args.dry_run, verbose=args.verbose)

    if "error" in stats:
        logger.error(stats["error"])
        return 1

    print_summary(stats, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
