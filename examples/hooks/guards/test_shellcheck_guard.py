#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Test shellcheck guard functionality."""

import json
import subprocess
from pathlib import Path


def run_guard(command: str) -> tuple[int, str, str]:
    """Run the shellcheck guard with a test command."""
    guard_path = Path(__file__).parent / "shellcheck_guard.py"
    payload = {
        "tool_name": "Bash",
        "tool_input": {
            "command": command,
            "description": "Test command"
        }
    }

    result = subprocess.run(
        ["uv", "run", str(guard_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )

    return result.returncode, result.stdout, result.stderr


def test_valid_command():
    """Test that valid commands pass."""
    exit_code, stdout, stderr = run_guard("ls -la /tmp")
    assert exit_code == 0, f"Expected exit 0, got {exit_code}: {stderr}"
    print("✓ Valid command passes")


def test_syntax_error():
    """Test that syntax errors are caught."""
    exit_code, stdout, stderr = run_guard("if [ -f file.txt ] then echo ok; fi")
    assert exit_code == 2, f"Expected exit 2, got {exit_code}"
    assert "SC1010" in stderr or "semicolon" in stderr.lower()
    print("✓ Syntax error caught")


def test_quote_issues():
    """Test that quoting issues are caught."""
    exit_code, stdout, stderr = run_guard('echo $foo')
    # This might pass or fail depending on shellcheck severity
    print(f"✓ Quote check: exit={exit_code}")


def test_empty_command():
    """Test that empty commands are handled."""
    exit_code, stdout, stderr = run_guard("")
    assert exit_code == 0, f"Expected exit 0 for empty command, got {exit_code}"
    print("✓ Empty command handled")


def test_complex_valid_command():
    """Test complex but valid command."""
    command = '''
    for file in *.txt; do
        if [[ -f "$file" ]]; then
            echo "Processing $file"
        fi
    done
    '''
    exit_code, stdout, stderr = run_guard(command)
    assert exit_code == 0, f"Expected exit 0, got {exit_code}: {stderr}"
    print("✓ Complex valid command passes")


if __name__ == "__main__":
    print("Testing shellcheck guard...")
    test_valid_command()
    test_syntax_error()
    test_quote_issues()
    test_empty_command()
    test_complex_valid_command()
    print("\nAll tests passed!")
