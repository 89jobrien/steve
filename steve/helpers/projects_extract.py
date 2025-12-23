"""Extract normalized events from ~/.claude/projects/*.jsonl.

Goal: turn Claude Code project JSONL into rows suitable for RL/FT.

- No side effects.
- Stdlib only.

The raw JSONL format is not stable across versions; this extractor is tolerant and
best-effort.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MessageEvent:
    session_id: str | None
    uuid: str | None
    parent_uuid: str | None
    timestamp: str | None
    role: str | None  # "user" | "assistant" | ...
    text: str


@dataclass(frozen=True)
class ToolUseEvent:
    session_id: str | None
    uuid: str | None
    parent_uuid: str | None
    timestamp: str | None
    role: str  # "assistant"
    tool_name: str
    tool_use_id: str | None
    tool_input: dict[str, Any]


@dataclass(frozen=True)
class ToolResultEvent:
    session_id: str | None
    uuid: str | None
    parent_uuid: str | None
    timestamp: str | None
    role: str  # "user"
    tool_use_id: str | None
    is_error: bool
    content_text: str


NormalizedEvent = MessageEvent | ToolUseEvent | ToolResultEvent


def iter_jsonl(path: Path) -> Iterator[dict[str, Any]]:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if isinstance(obj, dict):
                yield obj


def _get_str(d: dict[str, Any], k: str) -> str | None:
    v = d.get(k)
    return v if isinstance(v, str) else None


def _extract_text_from_message(message: Any) -> str:
    """Best-effort: flatten common message shapes to plain text."""
    if isinstance(message, str):
        return message

    if isinstance(message, dict):
        # canonical: {role, content}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            out: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    t = item.get("text")
                    if isinstance(t, str) and t:
                        out.append(t)
            return "\n".join(out).strip()

    return ""


def extract_events(record: dict[str, Any]) -> list[NormalizedEvent]:
    """Normalize a single JSONL record into 0..N events."""
    t = _get_str(record, "type")

    # Skip meta/synthetic records (e.g. local command echo + caveat boilerplate).
    # These are not useful for training and can dominate context.
    if record.get("isMeta") is True:
        return []

    # Some records are internal (snapshots, queue ops, summaries)
    if t in {"file-history-snapshot", "queue-operation", "summary"}:
        return []

    session_id = _get_str(record, "sessionId")
    uuid = _get_str(record, "uuid")
    parent_uuid = _get_str(record, "parentUuid")
    timestamp = _get_str(record, "timestamp")

    events: list[NormalizedEvent] = []

    # Top-level assistant/user wrapper has `message` field.
    msg = record.get("message")

    # Sometimes `message` is a dict (chat message); sometimes `message.content` is list.
    role: str | None = None
    if isinstance(msg, dict):
        role = _get_str(msg, "role")

    # 1) Tool use events (inside assistant message content)
    if role == "assistant" and isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "tool_use":
                    continue
                tool_name = item.get("name")
                tool_use_id = item.get("id")
                tool_input = item.get("input")
                if not isinstance(tool_name, str) or not tool_name:
                    continue
                if not isinstance(tool_use_id, str):
                    tool_use_id = None
                if not isinstance(tool_input, dict):
                    tool_input = {}

                events.append(
                    ToolUseEvent(
                        session_id=session_id,
                        uuid=uuid,
                        parent_uuid=parent_uuid,
                        timestamp=timestamp,
                        role="assistant",
                        tool_name=tool_name,
                        tool_use_id=tool_use_id,
                        tool_input=tool_input,
                    )
                )

    # 2) Tool result events (often in user message content)
    if isinstance(msg, dict):
        content = msg.get("content")
        if isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                if item.get("type") != "tool_result":
                    continue
                tool_use_id = item.get("tool_use_id")
                is_error = bool(item.get("is_error"))
                content_text = ""

                c = item.get("content")
                if isinstance(c, str):
                    content_text = c
                elif isinstance(c, list):
                    # common: list of {type:"text", text:"..."}
                    chunks: list[str] = []
                    for ch in c:
                        if isinstance(ch, dict) and ch.get("type") == "text":
                            tx = ch.get("text")
                            if isinstance(tx, str) and tx:
                                chunks.append(tx)
                    content_text = "\n".join(chunks)

                events.append(
                    ToolResultEvent(
                        session_id=session_id,
                        uuid=uuid,
                        parent_uuid=parent_uuid,
                        timestamp=timestamp,
                        role="user" if role is None else role,
                        tool_use_id=tool_use_id if isinstance(tool_use_id, str) else None,
                        is_error=is_error,
                        content_text=content_text.strip(),
                    )
                )

    # 3) Plain text messages (user/assistant)
    if isinstance(msg, dict) and role in {"user", "assistant"}:
        text = _extract_text_from_message(msg)
        if text:
            events.append(
                MessageEvent(
                    session_id=session_id,
                    uuid=uuid,
                    parent_uuid=parent_uuid,
                    timestamp=timestamp,
                    role=role,
                    text=text,
                )
            )

    return events


def iter_project_events(paths: Iterable[Path]) -> Iterator[NormalizedEvent]:
    for p in paths:
        for rec in iter_jsonl(p):
            yield from extract_events(rec)


def iter_project_files(projects_dir: Path) -> Iterator[Path]:
    yield from projects_dir.rglob("*.jsonl")
