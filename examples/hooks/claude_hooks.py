import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from hook_logging import log_error, log_info
except ImportError:
    # Fallback if hook_logging is not available
    def log_error(
        message: str,
        *,
        hook_name: str = "unknown",
        error: Exception | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        print(f"[HookError] {message}", file=sys.stderr)

    def log_info(
        message: str,
        *,
        hook_name: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> None:
        pass


@dataclass
class HookPayload:
    event: str
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    context: dict[str, str] | None = None
    timestamp: str | None = None


@dataclass
class HookResponse:
    allow: bool
    reason: str | None = None
    system_message: str | None = None
    updated_input: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> str:
        # Remove None values
        return json.dumps({k: v for k, v in asdict(self).items() if v is not None})


def list_hook_scripts() -> list[Path]:
    hooks_root = Path(__file__).parent
    scripts: list[Path] = []
    include_dirs = {
        hooks_root / "analyzers",
        hooks_root / "context",
        hooks_root / "guards",
        hooks_root / "lifecycle",
        hooks_root / "workflows",
    }
    for directory in include_dirs:
        for path in directory.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            if path.name.startswith("test_"):
                continue
            scripts.append(path)
    for path in hooks_root.glob("*.py"):
        if path.name in {"claude_hooks.py", "hook_logging.py", "test_hook_logging.py"}:
            continue
        if path.name.startswith("test_"):
            continue
        scripts.append(path)
    return sorted(set(scripts))


def run(handler):
    """
    Standard entry point for hooks.
    Reads payload from stdin, calls handler, and writes response to stdout.
    """
    hook_name = "unknown"
    raw_input = ""
    try:
        raw_input = sys.stdin.read()
        if not raw_input:
            return

        data = json.loads(raw_input)
        payload = HookPayload(**data)

        # Extract hook name from payload context if available
        if payload.context and "hook_name" in payload.context:
            hook_name = payload.context["hook_name"]

        response = handler(payload)

        if isinstance(response, HookResponse):
            print(response.to_json())
        else:
            print(json.dumps(response))

    except json.JSONDecodeError as e:
        log_error(
            "Failed to parse JSON payload",
            hook_name=hook_name,
            error=e,
            context={"raw_input_length": len(raw_input)},
        )
        print(json.dumps({"allow": True}))
    except Exception as e:
        log_error(
            "Unexpected error in hook execution",
            hook_name=hook_name,
            error=e,
            context={"error_type": type(e).__name__},
        )
        print(json.dumps({"allow": True}))
