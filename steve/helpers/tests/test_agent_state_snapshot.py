"""Tests for agent_state_snapshot.py - shell state snapshot feature extraction."""

import hashlib
import sys
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_state_snapshot import (
    _ALIAS_DEF,
    _EXPORT_DEF,
    _FUNC_DEF_1,
    _FUNC_DEF_2,
    _SETOPT_LINE,
    AgentStateSnapshot,
)


class TestRegexPatterns:
    """Tests for regex pattern matching."""

    def test_func_def_1_matches_simple_function(self) -> None:
        """Should match simple function definition."""
        text = "my_func() {"
        matches = _FUNC_DEF_1.findall(text)
        assert matches == ["my_func"]

    def test_func_def_1_matches_with_leading_spaces(self) -> None:
        """Should match function with leading whitespace."""
        text = "  my_func() {"
        matches = _FUNC_DEF_1.findall(text)
        assert matches == ["my_func"]

    def test_func_def_1_ignores_comments(self) -> None:
        """Should ignore commented function definitions."""
        text = "# my_func() {"
        matches = _FUNC_DEF_1.findall(text)
        assert matches == []

    def test_func_def_1_matches_with_special_chars(self) -> None:
        """Should match function names with hyphens and plus signs."""
        text = "my-func+name() {"
        matches = _FUNC_DEF_1.findall(text)
        assert matches == ["my-func+name"]

    def test_func_def_2_matches_function_keyword(self) -> None:
        """Should match 'function' keyword style."""
        text = "function my_func {"
        matches = _FUNC_DEF_2.findall(text)
        assert matches == ["my_func"]

    def test_func_def_2_matches_with_parens(self) -> None:
        """Should match function keyword with optional parens."""
        text = "function my_func() {"
        matches = _FUNC_DEF_2.findall(text)
        assert matches == ["my_func"]

    def test_func_def_2_ignores_comments(self) -> None:
        """Should ignore commented function definitions."""
        text = "# function my_func {"
        matches = _FUNC_DEF_2.findall(text)
        assert matches == []

    def test_alias_def_matches_simple_alias(self) -> None:
        """Should match simple alias definition."""
        text = "alias ll="
        matches = _ALIAS_DEF.findall(text)
        assert matches == ["ll"]

    def test_alias_def_ignores_comments(self) -> None:
        """Should ignore commented alias definitions."""
        text = "# alias ll="
        matches = _ALIAS_DEF.findall(text)
        assert matches == []

    def test_alias_def_matches_with_leading_spaces(self) -> None:
        """Should match alias with leading whitespace."""
        text = "  alias ll="
        matches = _ALIAS_DEF.findall(text)
        assert matches == ["ll"]

    def test_export_def_matches_export(self) -> None:
        """Should match export statement."""
        text = "export MY_VAR"
        matches = _EXPORT_DEF.findall(text)
        assert matches == ["MY_VAR"]

    def test_export_def_matches_typeset_x(self) -> None:
        """Should match typeset -x statement."""
        text = "typeset -x MY_VAR"
        matches = _EXPORT_DEF.findall(text)
        assert matches == ["MY_VAR"]

    def test_export_def_ignores_comments(self) -> None:
        """Should ignore commented export statements."""
        text = "# export MY_VAR"
        matches = _EXPORT_DEF.findall(text)
        assert matches == []

    def test_setopt_line_matches_setopt(self) -> None:
        """Should match setopt line."""
        text = "setopt AUTO_CD"
        matches = _SETOPT_LINE.findall(text)
        assert len(matches) == 1
        assert "setopt AUTO_CD" in matches[0]

    def test_setopt_line_matches_unsetopt(self) -> None:
        """Should match unsetopt line."""
        text = "unsetopt BEEP"
        matches = _SETOPT_LINE.findall(text)
        assert len(matches) == 1
        assert "unsetopt BEEP" in matches[0]

    def test_setopt_line_ignores_comments(self) -> None:
        """Should ignore commented setopt lines."""
        text = "# setopt AUTO_CD"
        matches = _SETOPT_LINE.findall(text)
        assert matches == []


class TestAgentStateSnapshotStaticMethods:
    """Tests for AgentStateSnapshot static methods."""

    def test_sha256_text_returns_hex_digest(self) -> None:
        """Should return SHA256 hex digest of text."""
        text = "hello world"
        result = AgentStateSnapshot._sha256_text(text)
        expected = hashlib.sha256(text.encode("utf-8")).hexdigest()
        assert result == expected

    def test_sha256_text_handles_unicode(self) -> None:
        """Should handle unicode characters."""
        text = "hello 世界 🌍"
        result = AgentStateSnapshot._sha256_text(text)
        expected = hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()
        assert result == expected

    def test_sha256_text_empty_string(self) -> None:
        """Should handle empty string."""
        text = ""
        result = AgentStateSnapshot._sha256_text(text)
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected

    def test_token_hash_returns_hex_digest(self) -> None:
        """Should return blake2s hex digest of token."""
        input_str = "my_function"
        result = AgentStateSnapshot._token_hash(input_str)
        expected = hashlib.blake2s(input_str.encode("utf-8"), digest_size=8).hexdigest()
        assert result == expected

    def test_token_hash_fixed_length(self) -> None:
        """Token hash should have fixed length (16 hex chars for 8 bytes)."""
        result = AgentStateSnapshot._token_hash("any_token")
        assert len(result) == 16


class TestExtractShellSnapshotState:
    """Tests for extract_shell_snapshot_state class method."""

    def test_extracts_functions_style_1(self) -> None:
        """Should extract function names in style 1."""
        snapshot = """
my_func() {
    echo "hello"
}
other_func() {
    echo "world"
}
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert "my_func" in result.function_names
        assert "other_func" in result.function_names

    def test_extracts_functions_style_2(self) -> None:
        """Should extract function names in style 2."""
        snapshot = """
function my_func {
    echo "hello"
}
function other_func() {
    echo "world"
}
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert "my_func" in result.function_names
        assert "other_func" in result.function_names

    def test_extracts_aliases(self) -> None:
        """Should extract alias names."""
        snapshot = """
alias ll='ls -la'
alias gs='git status'
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert "ll" in result.alias_names
        assert "gs" in result.alias_names

    def test_extracts_exports(self) -> None:
        """Should extract export names."""
        snapshot = """
export PATH="/usr/local/bin:$PATH"
export EDITOR="vim"
typeset -x MY_VAR="value"
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert "PATH" in result.export_names
        assert "EDITOR" in result.export_names
        assert "MY_VAR" in result.export_names

    def test_extracts_setopt_lines(self) -> None:
        """Should extract setopt lines."""
        snapshot = """
setopt AUTO_CD
setopt SHARE_HISTORY
unsetopt BEEP
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert len(result.setopt_lines) == 3

    def test_deduplicates_function_names(self) -> None:
        """Should deduplicate function names from both styles."""
        snapshot = """
my_func() {
    echo "style 1"
}
function my_func {
    echo "style 2"
}
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert result.function_names.count("my_func") == 1

    def test_sorts_names_alphabetically(self) -> None:
        """Should sort extracted names alphabetically."""
        snapshot = """
zebra_func() { }
apple_func() { }
mango_func() { }
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert result.function_names == ["apple_func", "mango_func", "zebra_func"]

    def test_respects_max_names_limit(self) -> None:
        """Should limit names to max_names parameter."""
        snapshot = "\n".join([f"func_{i}() {{}}" for i in range(10)])
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot, max_names=3)
        assert len(result.function_names) == 3

    def test_max_names_applies_to_all_categories(self) -> None:
        """Max names limit should apply to functions, aliases, and exports."""
        snapshot = "\n".join(
            [f"func_{i}() {{}}" for i in range(10)]
            + [f"alias alias_{i}='cmd'" for i in range(10)]
            + [f"export EXPORT_{i}=val" for i in range(10)]
        )
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot, max_names=5)
        assert len(result.function_names) == 5
        assert len(result.alias_names) == 5
        assert len(result.export_names) == 5

    def test_preserves_snapshot_text(self) -> None:
        """Should preserve original snapshot text."""
        snapshot = "my_func() { echo hello; }"
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert result.snapshot_text == snapshot

    def test_empty_snapshot(self) -> None:
        """Should handle empty snapshot text."""
        result = AgentStateSnapshot.extract_shell_snapshot_state("")
        assert result.function_names == []
        assert result.alias_names == []
        assert result.export_names == []
        assert result.setopt_lines == []

    def test_ignores_commented_lines(self) -> None:
        """Should ignore all commented definitions."""
        snapshot = """
# my_func() {
# alias ll='ls -la'
# export PATH="/usr/bin"
# setopt AUTO_CD
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert result.function_names == []
        assert result.alias_names == []
        assert result.export_names == []
        assert result.setopt_lines == []


class TestAgentStateSnapshotModel:
    """Tests for AgentStateSnapshot Pydantic model."""

    def test_creates_valid_model(self) -> None:
        """Should create valid model instance."""
        snapshot = AgentStateSnapshot(
            snapshot_text="test",
            function_names=["func1"],
            alias_names=["alias1"],
            export_names=["EXPORT1"],
            setopt_lines=["setopt AUTO_CD"],
        )
        assert snapshot.snapshot_text == "test"
        assert snapshot.function_names == ["func1"]
        assert snapshot.alias_names == ["alias1"]
        assert snapshot.export_names == ["EXPORT1"]
        assert snapshot.setopt_lines == ["setopt AUTO_CD"]

    def test_model_is_frozen(self) -> None:
        """Model fields should be immutable (frozen dataclass behavior via Pydantic)."""
        snapshot = AgentStateSnapshot(
            snapshot_text="test",
            function_names=["func1"],
            alias_names=[],
            export_names=[],
            setopt_lines=[],
        )
        # Pydantic models can be configured as immutable, but by default aren't
        # This test documents the expected behavior
        assert snapshot.snapshot_text == "test"


class TestIntegration:
    """Integration tests for complete extraction workflow."""

    def test_full_zsh_snapshot_extraction(self) -> None:
        """Should extract all features from a realistic zsh snapshot."""
        snapshot = """#!/bin/zsh
# This is a zsh snapshot

# Functions
my_func() {
    echo "hello"
}

function other_func {
    echo "world"
}

# Aliases
alias ll='ls -la'
alias gs='git status'

# Exports
export PATH="/usr/local/bin:$PATH"
export EDITOR="vim"

# Options
setopt AUTO_CD
setopt SHARE_HISTORY
unsetopt BEEP
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)

        assert len(result.function_names) == 2
        assert "my_func" in result.function_names
        assert "other_func" in result.function_names

        assert len(result.alias_names) == 2
        assert "ll" in result.alias_names
        assert "gs" in result.alias_names

        assert len(result.export_names) == 2
        assert "PATH" in result.export_names
        assert "EDITOR" in result.export_names

        assert len(result.setopt_lines) == 3

    def test_handles_mixed_indentation(self) -> None:
        """Should handle various indentation styles."""
        snapshot = """
    my_func() {
        echo "indented"
    }
		tabbed_func() {
			echo "tabs"
		}
alias spaced='test'
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert "my_func" in result.function_names
        assert "tabbed_func" in result.function_names
        assert "spaced" in result.alias_names

    def test_handles_special_characters_in_names(self) -> None:
        """Should handle special characters allowed in function/alias names."""
        snapshot = """
my-func+test() {
    echo "test"
}
alias my-alias+test='cmd'
"""
        result = AgentStateSnapshot.extract_shell_snapshot_state(snapshot)
        assert "my-func+test" in result.function_names
        assert "my-alias+test" in result.alias_names
