#!/usr/bin/env python3
"""Extract tool calls from transcript JSONL files."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, TextIO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract tool calls from transcript JSONL files."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=Path("transcripts"),
        help="Directory containing transcript JSONL files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("transcripts/tool_calls.jsonl"),
        help="Output JSONL file for tool call records.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the output file if it already exists.",
    )
    parser.add_argument(
        "--snippet-start",
        type=int,
        default=50,
        help="Start index for tool_output_snippet slicing.",
    )
    parser.add_argument(
        "--snippet-length",
        type=int,
        default=0,
        help="Optional length for tool_output_snippet (0 means no limit).",
    )
    return parser.parse_args()


def iter_transcript_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        msg = f"Input directory does not exist: {input_dir}"
        raise FileNotFoundError(msg)
    if not input_dir.is_dir():
        msg = f"Input path is not a directory: {input_dir}"
        raise NotADirectoryError(msg)
    return sorted(
        path
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix == ".jsonl"
    )


def extract_tool_calls_from_file(
    path: Path,
    writer: TextIO,
    snippet_start: int,
    snippet_length: int,
) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                record = json.loads(stripped)
            except json.JSONDecodeError:
                logging.warning("Skipping invalid JSON: %s:%s", path, line_number)
                continue
            record_type = record.get("type")
            if record_type not in {"tool_use", "tool_result"}:
                continue
            output = _format_tool_event(
                record,
                path,
                line_number,
                snippet_start,
                snippet_length,
            )
            writer.write(json.dumps(output, ensure_ascii=False) + "\n")
            count += 1
    return count


def _format_tool_event(
    record: dict[str, Any],
    path: Path,
    line_number: int,
    snippet_start: int,
    snippet_length: int,
) -> dict[str, Any]:
    tool_output = record.get("tool_output")
    output_str = "" if tool_output is None else json.dumps(tool_output, ensure_ascii=False)
    snippet = output_str[snippet_start:]
    if snippet_length > 0:
        snippet = snippet[:snippet_length]
    return {
        "session_id": path.stem,
        "source_file": str(path),
        "line_number": line_number,
        "timestamp": record.get("timestamp"),
        "type": record.get("type"),
        "tool_name": record.get("tool_name"),
        "tool_input": record.get("tool_input"),
        "tool_output": tool_output,
        "tool_output_snippet": snippet,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args = parse_args()
    input_dir = args.input_dir
    output_path = args.output

    if output_path.exists() and not args.overwrite:
        logging.error("Output file already exists: %s", output_path)
        raise SystemExit(1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_files = iter_transcript_files(input_dir)

    if not transcript_files:
        logging.warning("No transcript files found in %s", input_dir)

    total = 0
    with output_path.open("w", encoding="utf-8") as writer:
        for transcript_path in transcript_files:
            total += extract_tool_calls_from_file(
                transcript_path,
                writer,
                args.snippet_start,
                args.snippet_length,
            )

    logging.info("Wrote %s tool calls to %s", total, output_path)


if __name__ == "__main__":
    main()
