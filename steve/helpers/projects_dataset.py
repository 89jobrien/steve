"""Build RL/FT dataset rows from ~/.claude/projects/*.jsonl.

Row shape (JSON-serializable):
{session_id, t, messages, tool_name, tool_input, tool_result, trace, reward}

Notes:
- Best-effort: Claude Code JSONL schemas vary by version.
- Non-PII: this does not attempt to redact; do that downstream if needed.
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

from steve.helpers.projects_extract import (
    MessageEvent,
    ToolResultEvent,
    ToolUseEvent,
    iter_project_events,
)


@dataclass(frozen=True)
class DatasetRow:
    """A single row in the RL/FT dataset representing a tool use and its result."""

    session_id: str
    t: str | None
    messages: list[dict[str, Any]]
    tool_name: str
    tool_input: dict[str, Any]
    tool_result: dict[str, Any]
    trace: list[dict[str, Any]]
    reward: float


def _reward_from_tool_result(tool_result: ToolResultEvent) -> float:
    # Minimal proxy reward; you can replace/augment with hook-logs later.
    return -1.0 if tool_result.is_error else 1.0


def _msg_to_dict(m: MessageEvent) -> dict[str, Any]:
    return {
        "t": m.timestamp,
        "role": m.role,
        "text": m.text,
        "uuid": m.uuid,
        "parent_uuid": m.parent_uuid,
    }


def _tool_use_to_dict(tu: ToolUseEvent) -> dict[str, Any]:
    return {
        "type": "tool_use",
        "t": tu.timestamp,
        "tool_name": tu.tool_name,
        "tool_use_id": tu.tool_use_id,
        "tool_input": tu.tool_input,
        "uuid": tu.uuid,
        "parent_uuid": tu.parent_uuid,
    }


def _tool_result_to_dict(tr: ToolResultEvent) -> dict[str, Any]:
    return {
        "type": "tool_result",
        "t": tr.timestamp,
        "tool_use_id": tr.tool_use_id,
        "is_error": tr.is_error,
        "content_text": tr.content_text,
        "uuid": tr.uuid,
        "parent_uuid": tr.parent_uuid,
    }


@dataclass
class _PendingTool:
    tool_use: ToolUseEvent
    messages: list[MessageEvent]
    trace: list[dict[str, Any]]


def iter_dataset_rows_from_events(
    events: Iterable[MessageEvent | ToolUseEvent | ToolResultEvent],
    *,
    max_context_messages: int = 50,
    include_messages_in_trace: bool = True,
) -> Iterator[dict[str, Any]]:
    """Pair tool_use/tool_result into dataset rows.

    - `messages` captures the recent chat context at time of tool_use.
    - `trace` captures tool_use + tool_result (and optionally messages).
    """
    recent_messages: deque[MessageEvent] = deque(maxlen=max_context_messages)
    pending_by_id: dict[str, _PendingTool] = {}

    # Fallback IDs for tool_use events lacking tool_use_id.
    anon_counter = 0

    for ev in events:
        if isinstance(ev, MessageEvent):
            recent_messages.append(ev)
            if include_messages_in_trace:
                # If you want, you can enrich the trace for ALL pending tools.
                msg_dict = {
                    "type": "message",
                    "t": ev.timestamp,
                    "role": ev.role,
                    "text": ev.text,
                    "uuid": ev.uuid,
                    "parent_uuid": ev.parent_uuid,
                }
                for p in pending_by_id.values():
                    p.trace.append(msg_dict)
            continue

        if isinstance(ev, ToolUseEvent):
            anon_counter += 1
            tid = ev.tool_use_id or f"anon:{ev.uuid or 'no-uuid'}:{anon_counter}"
            pending_by_id[tid] = _PendingTool(
                tool_use=ev,
                messages=list(recent_messages),
                trace=[_tool_use_to_dict(ev)],
            )
            continue

        if isinstance(ev, ToolResultEvent):
            if not ev.tool_use_id:
                continue
            pending = pending_by_id.pop(ev.tool_use_id, None)
            if pending is None:
                continue

            pending.trace.append(_tool_result_to_dict(ev))

            session_id = pending.tool_use.session_id or ""
            row = DatasetRow(
                session_id=session_id,
                t=pending.tool_use.timestamp or ev.timestamp,
                messages=[_msg_to_dict(m) for m in pending.messages],
                tool_name=pending.tool_use.tool_name,
                tool_input=pending.tool_use.tool_input,
                tool_result=_tool_result_to_dict(ev),
                trace=pending.trace,
                reward=_reward_from_tool_result(ev),
            )
            yield asdict(row)


def iter_dataset_rows(
    project_files: Iterable[Path],
    *,
    max_context_messages: int = 50,
    include_messages_in_trace: bool = False,
) -> Iterator[dict[str, Any]]:
    """Iterate over dataset rows extracted from project JSONL files."""
    events = iter_project_events(project_files)
    yield from iter_dataset_rows_from_events(
        events,
        max_context_messages=max_context_messages,
        include_messages_in_trace=include_messages_in_trace,
    )


def write_jsonl(rows: Iterable[dict[str, Any]], out_path: Path) -> None:
    """Write dataset rows to a JSONL file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main(argv: list[str]) -> int:
    """CLI entry point for building dataset from project files."""
    if len(argv) < 3:
        msg = "usage: projects_dataset.py OUT.jsonl PROJECT.jsonl [PROJECT2.jsonl ...]"
        raise SystemExit(msg)

    out = Path(argv[1]).expanduser()
    files = [Path(p).expanduser() for p in argv[2:]]
    rows = iter_dataset_rows(files)
    write_jsonl(rows, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv))
