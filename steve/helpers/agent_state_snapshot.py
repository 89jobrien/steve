"""Inert feature extraction for agent "state" snapshots.

Option A: treat shell snapshots and related artifacts as *text* and extract
stable, deterministic features (no sourcing/execution).

Primary use:
- RL / fine-tuning datasets for tool-use policies.

This module intentionally does **not** execute shell code.
"""

from __future__ import annotations

import hashlib
import re

from pydantic import BaseModel


_FUNC_DEF_1 = re.compile(r"(?m)^(?!\s*#)\s*([A-Za-z_][A-Za-z0-9_+-]*)\s*\(\)\s*\{")
_FUNC_DEF_2 = re.compile(r"(?m)^(?!\s*#)\s*function\s+([A-Za-z_][A-Za-z0-9_+-]*)\s*(?:\(\))?\s*\{")
_ALIAS_DEF = re.compile(r"(?m)^(?!\s*#)\s*alias\s+([A-Za-z_][A-Za-z0-9_+-]*)=")
_EXPORT_DEF = re.compile(r"(?m)^(?!\s*#)\s*(?:export|typeset\s+-x)\s+([A-Za-z_][A-Za-z0-9_]*)")
_SETOPT_LINE = re.compile(r"(?m)^(?!\s*#)\s*(?:un)?setopt\b.*$")


class AgentStateSnapshot(BaseModel):
    """Parsed representation of a shell state snapshot."""

    snapshot_text: str
    function_names: list[str]
    alias_names: list[str]
    export_names: list[str]
    setopt_lines: list[str]

    def __post_init__(self) -> None:
        """Compute derived fields after initialization."""
        self.sha256 = self._sha256_text(self.snapshot_text)
        self.bytes = len(self.snapshot_text.encode("utf-8", "replace"))
        self.line_count = self.snapshot_text.count("\n") + 1
        self.function_count = len(self.function_names)
        self.alias_count = len(self.alias_names)
        self.export_count = len(self.export_names)
        self.setopt_line_count = len(self.setopt_lines)

    @staticmethod
    def _sha256_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()

    @staticmethod
    def _token_hash(token: str) -> str:
        h = hashlib.blake2s(token.encode("utf-8", "replace"), digest_size=8)
        return h.hexdigest()

    @classmethod
    def extract_shell_snapshot_state(
        cls, snapshot_text: str, *, max_names: int = 500
    ) -> AgentStateSnapshot:
        """Extract AgentStateSnapshot from a zsh snapshot script."""
        fn_names = set(_FUNC_DEF_1.findall(snapshot_text)) | set(_FUNC_DEF_2.findall(snapshot_text))
        alias_names = set(_ALIAS_DEF.findall(snapshot_text))
        export_names = set(_EXPORT_DEF.findall(snapshot_text))
        fn_names_sorted = sorted(fn_names)
        alias_names_sorted = sorted(alias_names)
        export_names_sorted = sorted(export_names)
        setopt_lines = _SETOPT_LINE.findall(snapshot_text)
        fn_cap = fn_names_sorted[:max_names]
        alias_cap = alias_names_sorted[:max_names]
        export_cap = export_names_sorted[:max_names]

        return AgentStateSnapshot(
            snapshot_text=snapshot_text,
            function_names=fn_cap,
            alias_names=alias_cap,
            export_names=export_cap,
            setopt_lines=setopt_lines,
        )
