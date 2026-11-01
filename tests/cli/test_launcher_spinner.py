"""The launcher startup animation hands off cleanly to the native client."""

import importlib
from unittest.mock import MagicMock
from urllib.error import URLError

import pytest

from free_claude_code.cli.launchers import runner
from tests.cli.conftest import LaunchCapture


def _launch(name: str, args: list[str]) -> int:
    module = importlib.import_module(f"free_claude_code.cli.launchers.{name}")
    with pytest.raises(SystemExit) as exc:
        module.launch(args)
    return exc.value.code


def _describe_spinner(monkeypatch, order, created):
    """Swap in a recording spinner and capture the message it shows."""
    instance = MagicMock()
    instance.start.side_effect = lambda: order.append("start")
    instance.stop.side_effect = lambda *args: order.append("stop")
    monkeypatch.setattr(
        runner,
        "StartupAnimation",
        lambda message: (created.append(message), instance)[1],
    )
    return instance


def test_spinner_animates_until_the_client_handoff(
    launch_capture: LaunchCapture, monkeypatch
):
    order: list[str] = []
    created: list[str] = []
    spinner = _describe_spinner(monkeypatch, order, created)

    def handoff(**kwargs):
        order.append("handoff")
        raise SystemExit(launch_capture.exit_code)

    monkeypatch.setattr(runner, "run_client_process", handoff)

    assert _launch("claude", []) == launch_capture.exit_code
    assert created == ["Starting Claude Code..."]
    spinner.start.assert_called_once_with()
    # The animation stops before the client TUI starts, then again on teardown.
    assert order == ["start", "stop", "handoff", "stop"]


def test_spinner_is_cleared_before_reporting_setup_failure(
    launch_capture: LaunchCapture, monkeypatch, capsys
):
    order: list[str] = []
    _describe_spinner(monkeypatch, order, [])
    launch_capture.health_error = URLError("test server is stopped")

    assert _launch("claude", []) == 1
    # The failed preflight stops the animation before the error reaches stderr.
    assert order[:2] == ["start", "stop"]
    assert "Free Claude Code proxy is not reachable" in capsys.readouterr().err


def test_fast_setup_failure_never_starts_the_spinner(
    launch_capture: LaunchCapture, monkeypatch, capsys
):
    import sys

    order: list[str] = []
    created: list[str] = []
    spinner = _describe_spinner(monkeypatch, order, created)

    def missing_binary(**kwargs):
        print("Could not find Codex command: codex", file=sys.stderr)
        raise SystemExit(127)

    monkeypatch.setattr(runner, "resolve_client_binary", missing_binary)

    assert _launch("codex", []) == 127
    # The binary lookup reports its own error before any animation could draw.
    assert order == ["stop"]
    spinner.start.assert_not_called()
    assert created == ["Starting Codex CLI..."]
    assert "Could not find Codex command" in capsys.readouterr().err
