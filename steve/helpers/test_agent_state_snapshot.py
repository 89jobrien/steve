# /// script
# requires-python = ">=3.12"
# ///
"""Tests for agent_state_snapshot module."""

from steve.helpers.agent_state_snapshot import AgentStateSnapshot


class TestAgentStateSnapshot:
    def test_extracts_functions_aliases_exports(self) -> None:
        text = """# Snapshot file
# comment: foo () { not a function }
unalias -a 2>/dev/null || true
foo () {
  echo hi
}
bar(){ :; }
function baz { :; }
alias ll='ls -la'
typeset -x PATH=/bin:/usr/bin
export HOME=/Users/joe
setopt NO_shwordsplit
"""

        st = AgentStateSnapshot.extract_shell_snapshot_state(text, max_names=500)

        assert len(st.snapshot_text) > 0
        assert len(st.function_names) == 3
        assert len(st.alias_names) == 1
        assert len(st.export_names) == 2
        assert len(st.setopt_lines) == 1

        assert st.function_names == ["bar", "baz", "foo"]
        assert st.alias_names == ["ll"]
        assert st.export_names == ["HOME", "PATH"]

    def test_is_deterministic(self) -> None:
        text = "foo () { :; }\nexport X=1\n"
        a = AgentStateSnapshot.extract_shell_snapshot_state(text)
        b = AgentStateSnapshot.extract_shell_snapshot_state(text)
        assert a == b
