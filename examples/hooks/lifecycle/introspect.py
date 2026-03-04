#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema"]
# ///

"""
Prompt critical self-review with improved error handling and validation.

This hook checks if a session included self-review markers.
Runs on Stop and SubagentStop events.

Features:
- JSON schema validation for payloads
- Structured logging with context
- Extensible marker detection (supports regex mode)
- Built-in test mode for local development
- TypedDict for type safety
- Lazy logging to avoid expensive operations
"""

import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from jsonschema import ValidationError, validate

HOOKS_ROOT = Path(__file__).parent.parent
if str(HOOKS_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402

# ============================================================================
# Type Definitions
# ============================================================================


class PayloadDict(TypedDict, total=False):
    """Typed payload structure for hook invocation."""

    stop_hook_active: bool
    transcript_path: str
    tool_input: dict


# ============================================================================
# Configuration & Schema
# ============================================================================


@dataclass
class ReviewConfig:
    """Configuration for self-review detection and question generation."""

    markers: tuple[str, ...]
    base_questions: list[str]
    code_questions: list[str]


CONFIG = ReviewConfig(
    markers=(
        "self review",
        "critical review",
        "implementation complete",
        "testing complete",
        "edge cases considered",
    ),
    base_questions=[
        "Have all requested features been fully implemented?",
        "Are error cases and edge conditions properly handled?",
        "Have you tested the implementation with various inputs?",
        "Is the code documented and readable?",
        "Are there any performance or security concerns?",
    ],
    code_questions=[
        "Are type hints/types properly defined?",
        "Is there adequate test coverage?",
        "Are there obvious performance improvements?",
    ],
)

# JSON Schema for payload validation
PAYLOAD_SCHEMA = {
    "type": "object",
    "properties": {
        "stop_hook_active": {"type": "boolean"},
        "transcript_path": {"type": "string"},
        "tool_input": {
            "oneOf": [
                {"type": "object"},
                {"type": "null"},
            ]
        },
    },
    "required": ["transcript_path"],
    "additionalProperties": True,  # Allow extra fields
}

# Supported code file extensions
CODE_EXTENSIONS = {".py", ".ts", ".js", ".tsx", ".jsx", ".go", ".rs", ".sh", ".zsh"}


# ============================================================================
# Core Functions
# ============================================================================


def normalize_content(content: str) -> str:
    """
    Normalize content for marker matching.

    Converts to lowercase and replaces dashes/underscores with spaces
    for flexible marker matching.

    Args:
        content: Raw text to normalize

    Returns:
        Normalized text
    """
    return content.lower().replace("-", " ").replace("_", " ")


def check_for_self_review_marker(
    content: str,
    markers: tuple[str, ...],
    case_sensitive: bool = False,
    recent_lines_only: int | None = None,
) -> bool:
    """
    Check if content contains any self-review markers.

    Supports checking recent lines only for performance with large transcripts.

    Args:
        content: Text to search
        markers: Marker strings to find
        case_sensitive: Whether to match case (default: False)
        recent_lines_only: If set, only check last N lines of content

    Returns:
        True if any marker found, False otherwise
    """
    # Optimize for large files by checking recent lines only
    if recent_lines_only is not None:
        lines = content.split("\n")
        content = "\n".join(lines[-recent_lines_only:])

    if case_sensitive:
        return any(marker in content for marker in markers)

    normalized = normalize_content(content)
    return any(marker in normalized for marker in markers)


def generate_review_questions(
    file_path: str | None,
    config: ReviewConfig,
) -> list[str]:
    """
    Generate relevant review questions based on context.

    Adds language-specific questions for code files.

    Args:
        file_path: Optional file path being reviewed
        config: ReviewConfig with question templates

    Returns:
        List of relevant review questions
    """
    questions = config.base_questions.copy()

    if file_path:
        path = Path(file_path)
        if path.suffix in CODE_EXTENSIONS:
            questions.extend(config.code_questions)

    return questions


def validate_payload(payload: dict) -> tuple[bool, str | None]:
    """
    Validate payload against schema.

    Args:
        payload: Payload dict to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        validate(instance=payload, schema=PAYLOAD_SCHEMA)
        return True, None
    except ValidationError as e:
        return False, f"Payload validation failed: {e.message}"


def process_payload(
    payload: dict,
    logger: logging.Logger,
) -> list[str] | None:
    """
    Core processing logic - returns questions if review needed, else None.

    Performs validation, reads transcript, checks for markers, and generates
    questions as needed.

    Args:
        payload: Input payload dict
        logger: Logger instance for debug output

    Returns:
        List of review questions if review needed, None otherwise
    """
    # Validate payload structure
    is_valid, error_msg = validate_payload(payload)
    if not is_valid:
        logger.debug(error_msg)
        return None

    # Early exit: stop_hook_active
    if payload.get("stop_hook_active"):
        logger.debug("Skipping: stop_hook_active is set")
        return None

    # Early exit: missing transcript_path
    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        logger.debug("Skipping: no transcript_path in payload")
        return None

    # Validate path exists
    path = Path(transcript_path)
    if not path.exists():
        logger.debug(f"Transcript not found: {path}")
        return None

    # Read transcript content
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        logger.debug(f"Failed to read transcript: {e}")
        return None

    # Check for self-review marker (check last 500 lines for performance)
    if check_for_self_review_marker(content, CONFIG.markers, recent_lines_only=500):
        logger.debug("Self-review marker found in transcript")
        return None

    # Extract file_path from tool_input if present
    tool_input = payload.get("tool_input", {})
    file_path = None
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path")

    # Generate and return relevant questions
    questions = generate_review_questions(file_path, CONFIG)
    logger.debug(f"Generated {len(questions)} review questions")
    return questions


def setup_logging() -> logging.Logger:
    """
    Configure logging for hook output.

    Sets up stderr logging with warning level and structured formatting.
    Only configures if not already configured.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)

    # Only configure if not already configured (avoid duplicate handlers)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            "%(name)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.WARNING)
    return logger


def generate_structured_output(
    questions: list[str],
    payload: dict,
) -> dict:
    """
    Generate machine-readable structured output.

    Args:
        questions: Review questions to include
        payload: Original payload for context

    Returns:
        Structured output dict
    """
    tool_input = payload.get("tool_input", {})
    file_path = None
    if isinstance(tool_input, dict):
        file_path = tool_input.get("file_path")

    return {
        "kind": "self_review_missing",
        "severity": "warning",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "questions": questions,
        "transcript_path": str(payload.get("transcript_path")),
        "file_path": file_path,
        "question_count": len(questions),
    }


def main(test_mode: bool = False) -> None:
    """
    Main entry point for the hook.

    Reads JSON payload from stdin, processes it, and outputs results.
    Supports test mode for local development.

    Args:
        test_mode: If True, use sample payload instead of stdin
    """
    logger = setup_logging()

    try:
        # Load payload
        if test_mode:
            logger.info("Running in test mode with sample payload")
            payload = {
                "transcript_path": "/tmp/test_transcript.txt",
                "stop_hook_active": False,
                "tool_input": {"file_path": "example.py"},
            }
            # Create test transcript
            Path("/tmp/test_transcript.txt").write_text(
                "Session transcript\n"
                "The agent worked on implementing the feature.\n"
                "Code changes applied and tested.\n"
            )
        else:
            try:
                payload = json.load(sys.stdin)
            except json.JSONDecodeError as e:
                logger.debug(f"Invalid JSON input: {e}")
                sys.exit(0)

        # Process with hook invocation context
        with hook_invocation("self_review") as inv:
            inv.set_payload(payload)

            # Process payload
            questions = process_payload(payload, logger)

            # Exit early if review not needed
            if not questions:
                sys.exit(0)

            # Generate and output structured message to stdout (so Claude can read it)
            structured_msg = generate_structured_output(questions, payload)
            print(json.dumps(structured_msg, separators=(",", ":")))

            # Human-readable output
            logger.warning("No self-review detected in session")
            logger.info("Consider reviewing the following:")
            for i, question in enumerate(questions, 1):
                logger.info(f"  {i}. {question}")

    except Exception as e:
        logger.error(f"Unexpected error in self_review hook: {e}", exc_info=True)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    # Support --test flag for local testing
    test_mode = len(sys.argv) > 1 and sys.argv[1] == "--test"
    main(test_mode=test_mode)
