"""Convert projects dataset to OpenPipe ART trajectory format.

Transforms tool-use rows from build_projects_dataset.py into
trajectories suitable for GRPO training with OpenPipe ART.

Features:
- Groups tool calls by session into coherent trajectories
- Computes multi-signal rewards (tool success, efficiency, task completion)
- Filters warmup/noise messages
- Outputs ART-compatible JSONL

Example:
  uv run python scripts/projects_to_art.py \
    --input ~/.claude/datasets/projects_tool_rows.jsonl \
    --output ~/.claude/datasets/lisa_trajectories.jsonl \
    --min-trajectory-length 3 \
    --max-trajectory-length 50
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Allow running as a script
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@dataclass
class ToolCall:
    """Single tool invocation within a trajectory."""

    name: str
    input: dict[str, Any]
    result: str | dict[str, Any]
    success: bool
    timestamp: str


@dataclass
class TrajectoryRewards:
    """Multi-signal reward structure for GRPO training."""

    tool_success_rate: float = 0.0  # % of tool calls that succeeded
    efficiency: float = 0.0  # Fewer calls = higher efficiency
    task_completed: float = 0.0  # From TodoWrite status transitions
    error_recovery: float = 0.0  # Handled errors gracefully
    code_quality: float = 0.0  # Reserved for RULER/lint scores

    def combined(self, weights: dict[str, float] | None = None) -> float:
        """Compute weighted combined reward."""
        w = weights or {
            "tool_success_rate": 0.3,
            "efficiency": 0.2,
            "task_completed": 0.3,
            "error_recovery": 0.1,
            "code_quality": 0.1,
        }
        total = 0.0
        weight_sum = 0.0
        for key, weight in w.items():
            val = getattr(self, key, 0.0)
            if val > 0 or key in ("tool_success_rate", "efficiency"):
                total += weight * val
                weight_sum += weight
        return total / weight_sum if weight_sum > 0 else 0.5


@dataclass
class LisaTrajectory:
    """OpenPipe ART trajectory for Lisa AI code completion training."""

    session_id: str
    messages: list[dict[str, str]] = field(default_factory=list)
    tool_calls: list[ToolCall] = field(default_factory=list)
    rewards: TrajectoryRewards = field(default_factory=TrajectoryRewards)
    final_reward: float = 0.0

    # Optional context metadata
    file_paths: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    def to_art_format(self) -> dict[str, Any]:
        """Convert to OpenPipe ART trajectory dict."""
        messages_and_choices = []

        # Add system prompt
        messages_and_choices.append({
            "role": "system",
            "content": self._generate_system_prompt(),
        })

        # Interleave messages and tool calls
        for msg in self.messages:
            messages_and_choices.append({
                "role": msg.get("role", "user"),
                "content": msg.get("text", ""),
            })

        # Tool calls become assistant choices with tool_calls field
        for tc in self.tool_calls:
            # Assistant message with tool call
            messages_and_choices.append({
                "role": "assistant",
                "content": "",
                "tool_calls": [{
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.input),
                    },
                }],
            })
            # Tool response
            result_str = tc.result if isinstance(tc.result, str) else json.dumps(tc.result)
            messages_and_choices.append({
                "role": "tool",
                "content": result_str[:2000],  # Truncate large results
                "name": tc.name,
            })

        return {
            "reward": self.final_reward,
            "messages_and_choices": messages_and_choices,
            "metadata": {
                "session_id": self.session_id,
                "file_paths": self.file_paths,
                "languages": self.languages,
                "rewards_breakdown": asdict(self.rewards),
                "num_tool_calls": len(self.tool_calls),
            },
        }

    def _generate_system_prompt(self) -> str:
        """Generate context-aware system prompt."""
        langs = ", ".join(set(self.languages)) if self.languages else "code"
        return f"""You are Lisa AI, an intelligent code completion assistant.

You have access to tools for:
- Reading files (Read)
- Editing files (Edit)
- Running commands (Bash)
- Searching code (Grep, Glob)
- Managing tasks (TodoWrite)

Current context: Working with {langs} files.

Provide helpful, accurate code completions. Use tools efficiently -
gather context first, then make targeted edits."""


# Tool categories for reward computation
TOOL_CATEGORIES = {
    "context": {"Read", "Glob", "Grep", "WebFetch"},
    "modification": {"Edit", "Write", "MultiEdit"},
    "execution": {"Bash", "BashOutput"},
    "task": {"TodoWrite", "Task", "TaskOutput"},
    "mcp": set(),  # Dynamically detected
}

# Error indicators in tool results
ERROR_PATTERNS = [
    "error",
    "Error",
    "ERROR",
    "failed",
    "Failed",
    "FAILED",
    "not found",
    "does not exist",
    "permission denied",
    "timed out",
]


def is_tool_error(result: str | dict[str, Any]) -> bool:
    """Check if tool result indicates an error."""
    result_str = result if isinstance(result, str) else json.dumps(result)
    return any(pattern in result_str for pattern in ERROR_PATTERNS)


def extract_file_path(tool_input: dict[str, Any]) -> str | None:
    """Extract file path from tool input if present."""
    for key in ("file_path", "path", "file"):
        if key in tool_input:
            return tool_input[key]
    return None


def detect_language(file_path: str) -> str | None:
    """Detect programming language from file extension."""
    ext_map = {
        ".py": "python",
        ".go": "go",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".rs": "rust",
        ".rb": "ruby",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".md": "markdown",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
    }
    ext = Path(file_path).suffix.lower()
    return ext_map.get(ext)


def is_warmup_message(msg: dict[str, Any]) -> bool:
    """Filter out warmup/noise messages."""
    text = msg.get("text", "")
    if not text:
        return True
    warmup_patterns = [
        "Warmup",
        "memory agent",
        "MEMORY PROCESSING",
        "observed_from_primary_session",
        "Claude-Mem",
    ]
    return any(p in text for p in warmup_patterns)


def compute_rewards(trajectory: LisaTrajectory) -> TrajectoryRewards:
    """Compute multi-signal rewards for a trajectory."""
    rewards = TrajectoryRewards()

    if not trajectory.tool_calls:
        return rewards

    # Tool success rate
    successes = sum(1 for tc in trajectory.tool_calls if tc.success)
    rewards.tool_success_rate = successes / len(trajectory.tool_calls)

    # Efficiency (fewer calls for context+modification pattern is better)
    # Baseline: 5 context + 2 modification = 7 calls
    expected_calls = 7
    actual = len(trajectory.tool_calls)
    rewards.efficiency = max(0.0, min(1.0, expected_calls / max(actual, 1)))

    # Task completion from TodoWrite
    todo_calls = [tc for tc in trajectory.tool_calls if tc.name == "TodoWrite"]
    if todo_calls:
        # Check if any todo was marked completed
        for tc in todo_calls:
            input_data = tc.input
            todos = input_data.get("todos", [])
            completed = sum(1 for t in todos if t.get("status") == "completed")
            if completed > 0:
                rewards.task_completed = 1.0
                break

    # Error recovery: errors followed by successful retry
    for i, tc in enumerate(trajectory.tool_calls[:-1]):
        if not tc.success:
            next_tc = trajectory.tool_calls[i + 1]
            if next_tc.name == tc.name and next_tc.success:
                rewards.error_recovery = 0.5
                break

    return rewards


def group_rows_by_session(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group dataset rows by session_id."""
    sessions: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        sid = row.get("session_id", "unknown")
        sessions[sid].append(row)

    # Sort each session by timestamp
    for sid in sessions:
        sessions[sid].sort(key=lambda r: r.get("t", ""))

    return sessions


def build_trajectory(
    session_id: str,
    rows: list[dict[str, Any]],
    max_length: int = 50,
) -> LisaTrajectory:
    """Build a LisaTrajectory from session rows."""
    traj = LisaTrajectory(session_id=session_id)

    # Collect unique messages (dedupe by uuid)
    seen_uuids: set[str] = set()
    for row in rows[:max_length]:
        for msg in row.get("messages", []):
            uuid = msg.get("uuid")
            if uuid and uuid not in seen_uuids and not is_warmup_message(msg):
                seen_uuids.add(uuid)
                traj.messages.append({
                    "role": msg.get("role", "user"),
                    "text": msg.get("text", ""),
                    "timestamp": msg.get("t", ""),
                })

    # Collect tool calls
    for row in rows[:max_length]:
        tool_name = row.get("tool_name", "")
        tool_input = row.get("tool_input", {})
        tool_result = row.get("tool_result", "")

        # Parse tool_input if it's a string
        if isinstance(tool_input, str):
            try:
                tool_input = json.loads(tool_input)
            except json.JSONDecodeError:
                tool_input = {"raw": tool_input}

        success = not is_tool_error(tool_result)

        tc = ToolCall(
            name=tool_name,
            input=tool_input,
            result=tool_result,
            success=success,
            timestamp=row.get("t", ""),
        )
        traj.tool_calls.append(tc)

        # Extract metadata
        file_path = extract_file_path(tool_input)
        if file_path:
            traj.file_paths.append(file_path)
            lang = detect_language(file_path)
            if lang:
                traj.languages.append(lang)

    # Dedupe file paths and languages
    traj.file_paths = list(dict.fromkeys(traj.file_paths))
    traj.languages = list(dict.fromkeys(traj.languages))

    # Compute rewards
    traj.rewards = compute_rewards(traj)
    traj.final_reward = traj.rewards.combined()

    return traj


def convert_dataset(
    input_path: Path,
    output_path: Path,
    min_length: int = 3,
    max_length: int = 50,
) -> dict[str, Any]:
    """Convert projects dataset to ART trajectories."""
    # Load input rows
    rows: list[dict[str, Any]] = []
    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    # Group by session
    sessions = group_rows_by_session(rows)

    # Build trajectories
    trajectories: list[LisaTrajectory] = []
    skipped = 0

    for session_id, session_rows in sessions.items():
        if len(session_rows) < min_length:
            skipped += 1
            continue

        traj = build_trajectory(session_id, session_rows, max_length)

        # Skip trajectories with no valid tool calls
        if len(traj.tool_calls) < min_length:
            skipped += 1
            continue

        trajectories.append(traj)

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for traj in trajectories:
            f.write(json.dumps(traj.to_art_format(), ensure_ascii=False) + "\n")

    # Compute stats
    stats = {
        "input_rows": len(rows),
        "sessions": len(sessions),
        "trajectories": len(trajectories),
        "skipped": skipped,
        "avg_tool_calls": (
            sum(len(t.tool_calls) for t in trajectories) / len(trajectories)
            if trajectories else 0
        ),
        "avg_reward": (
            sum(t.final_reward for t in trajectories) / len(trajectories)
            if trajectories else 0
        ),
        "language_distribution": _compute_lang_dist(trajectories),
        "tool_distribution": _compute_tool_dist(trajectories),
    }

    # Write stats
    stats_path = output_path.with_suffix(output_path.suffix + ".stats.json")
    stats_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return stats


def _compute_lang_dist(trajectories: list[LisaTrajectory]) -> dict[str, int]:
    """Compute language distribution across trajectories."""
    dist: dict[str, int] = defaultdict(int)
    for traj in trajectories:
        for lang in traj.languages:
            dist[lang] += 1
    return dict(sorted(dist.items(), key=lambda x: -x[1])[:20])


def _compute_tool_dist(trajectories: list[LisaTrajectory]) -> dict[str, int]:
    """Compute tool usage distribution."""
    dist: dict[str, int] = defaultdict(int)
    for traj in trajectories:
        for tc in traj.tool_calls:
            dist[tc.name] += 1
    return dict(sorted(dist.items(), key=lambda x: -x[1])[:20])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, required=True, help="Input JSONL from build_projects_dataset.py")
    ap.add_argument("--output", type=Path, required=True, help="Output ART trajectories JSONL")
    ap.add_argument("--min-trajectory-length", type=int, default=3, help="Min tool calls per trajectory")
    ap.add_argument("--max-trajectory-length", type=int, default=50, help="Max tool calls per trajectory")
    args = ap.parse_args()

    input_path = args.input.expanduser()
    output_path = args.output.expanduser()

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    print(f"Converting {input_path} -> {output_path}")
    stats = convert_dataset(
        input_path,
        output_path,
        min_length=args.min_trajectory_length,
        max_length=args.max_trajectory_length,
    )

    print(f"Created {stats['trajectories']} trajectories from {stats['sessions']} sessions")
    print(f"Average tool calls: {stats['avg_tool_calls']:.1f}")
    print(f"Average reward: {stats['avg_reward']:.3f}")
    print(f"Skipped: {stats['skipped']} (too short)")
    print(f"Stats written to {output_path.with_suffix(output_path.suffix + '.stats.json')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
