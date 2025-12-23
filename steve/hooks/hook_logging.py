#!/usr/bin/env python3
"""Shared hook invocation logging.

Design goals:
- One structured JSONL record per hook invocation (daily file)
- One short stderr breadcrumb per invocation
- No prompt/content logging (only minimal fields)
- Must work even when hooks call sys.exit()
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


def _get_session_id() -> str:
    return os.environ.get("CLAUDE_SESSION_ID", str(os.getpid()))


def _get_log_dir() -> Path:
    # Allow override for tests/local experimentation.
    override = os.environ.get("CLAUDE_HOOK_LOG_DIR")
    if override:
        p = Path(override).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p

    p = Path.home() / ".claude" / "logs"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _get_daily_log_path(now: datetime) -> Path:
    date_str = now.strftime("%Y%m%d")
    return _get_log_dir() / f"hooks_{date_str}.jsonl"


def _safe_str(v: Any, *, max_len: int = 200) -> str:
    try:
        s = str(v)
    except Exception:
        return "<unprintable>"
    return s if len(s) <= max_len else (s[: max_len - 3] + "...")


def _extract_payload_fields(payload: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}

    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        out["cwd"] = cwd

    tool_name = payload.get("tool_name")
    if isinstance(tool_name, str) and tool_name:
        out["tool_name"] = tool_name

    transcript_path = payload.get("transcript_path")
    if isinstance(transcript_path, str) and transcript_path:
        out["transcript_path"] = transcript_path

    stop_hook_active = payload.get("stop_hook_active")
    if isinstance(stop_hook_active, bool):
        out["stop_hook_active"] = stop_hook_active

    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path")
        if isinstance(file_path, str) and file_path:
            out["tool_input.file_path"] = file_path

    return out


@dataclass
class HookInvocation:
    hook_name: str
    start_wall: datetime
    start_mono: float
    payload_fields: dict[str, Any] = field(default_factory=dict)

    def set_payload(self, payload: dict[str, Any]) -> None:
        self.payload_fields = _extract_payload_fields(payload)


def _write_jsonl(record: dict[str, Any], now: datetime) -> None:
    try:
        path = _get_daily_log_path(now)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        # Logging must never break hook behavior.
        return


def _stderr_breadcrumb(record: dict[str, Any]) -> None:
    # Example:
    # [HookLog] hook=secret_scanner tool=Write file=... ok dur_ms=12 exit=0
    parts: list[str] = ["[HookLog]"]

    parts.append(f"hook={record.get('hook_name', '?')}")

    tool = record.get("tool_name")
    if tool:
        parts.append(f"tool={tool}")

    file_path = record.get("tool_input.file_path")
    if file_path:
        parts.append(f"file={_safe_str(file_path, max_len=120)}")

    parts.append("ok" if record.get("ok") else "fail")
    parts.append(f"dur_ms={record.get('duration_ms')}")
    parts.append(f"exit={record.get('exit_code')}")

    try:
        print(" ".join(parts), file=sys.stderr)
    except Exception:
        return


@contextmanager
def hook_invocation(hook_name: str) -> Iterator[HookInvocation]:
    start_wall = datetime.now()
    start_mono = time.monotonic()
    inv = HookInvocation(hook_name=hook_name, start_wall=start_wall, start_mono=start_mono)

    exit_code = 0
    ok = True
    exc_type: str | None = None
    exc_msg: str | None = None

    try:
        yield inv
    except SystemExit as e:
        code = e.code
        if code is None:
            exit_code = 0
        elif isinstance(code, int):
            exit_code = code
        else:
            exit_code = 1
            exc_type = "SystemExit"
            exc_msg = _safe_str(code)

        ok = exit_code == 0
        raise
    except Exception as e:
        exit_code = 1
        ok = False
        exc_type = type(e).__name__
        exc_msg = _safe_str(e)
        raise
    finally:
        end_wall = datetime.now()
        # Use rounding to avoid float truncation artifacts.
        duration_ms = int(round((time.monotonic() - start_mono) * 1000))

        record: dict[str, Any] = {
            "start_ts": start_wall.isoformat(),
            "end_ts": end_wall.isoformat(),
            # Back-compat / convenience (treat as start timestamp).
            "timestamp": start_wall.isoformat(),
            "hook_name": hook_name,
            "pid": os.getpid(),
            "session_id": _get_session_id(),
            "duration_ms": duration_ms,
            "exit_code": exit_code,
            "ok": ok,
        }
        record.update(inv.payload_fields)
        if exc_type:
            record["error_type"] = exc_type
        if exc_msg:
            record["error"] = exc_msg

        _write_jsonl(record, end_wall)
        _stderr_breadcrumb(record)
