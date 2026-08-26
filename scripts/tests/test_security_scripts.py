"""Isolated security regression tests for bundled skill scripts."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str, relative_path: str) -> ModuleType:
    script_path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, script_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


JIRA_API = load_script("jira_api_security_test", "steve/skills/jira/scripts/jira-api.py")
WITH_SERVER = load_script(
    "with_server_security_test", "steve/skills/testing/scripts/with-server.py"
)


@pytest.mark.parametrize(
    ("domain", "message"),
    [
        ("http://jira.example.com", "HTTPS"),
        ("https://user:password@jira.example.com", "embedded credentials"),
    ],
)
def test_jira_rejects_unsafe_url_before_loading_auth(
    monkeypatch: pytest.MonkeyPatch, domain: str, message: str
) -> None:
    monkeypatch.setenv("JIRA_DOMAIN", domain)

    def unexpected_call(*_args, **_kwargs):
        pytest.fail("unsafe Jira URL reached authenticated network setup")

    monkeypatch.setattr(JIRA_API, "get_auth_header", unexpected_call)
    monkeypatch.setattr(JIRA_API.urllib.request, "urlopen", unexpected_call)

    with pytest.raises(ValueError, match=message):
        JIRA_API.make_request("GET", "/issue/SEC-1")


def test_server_command_uses_intentional_shell_boundary(monkeypatch: pytest.MonkeyPatch) -> None:
    captured = {}
    sentinel = object()

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return sentinel

    monkeypatch.setattr(WITH_SERVER.subprocess, "Popen", fake_popen)

    result = WITH_SERVER.start_trusted_local_server("cd app && npm start")

    assert result is sentinel
    assert captured == {
        "command": "cd app && npm start",
        "shell": True,
        "stdout": WITH_SERVER.subprocess.PIPE,
        "stderr": WITH_SERVER.subprocess.PIPE,
    }
