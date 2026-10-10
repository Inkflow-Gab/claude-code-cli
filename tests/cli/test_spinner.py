"""Unit coverage for the non-interactive-safe startup animation."""

import io

from free_claude_code.cli import spinner


class _Stream(io.StringIO):
    """StringIO stand-in that reports whether it looks like a terminal."""

    def __init__(self, *, tty: bool) -> None:
        super().__init__()
        self._tty = tty

    def isatty(self) -> bool:
        return self._tty


def test_animation_is_skipped_off_terminal(monkeypatch):
    monkeypatch.delenv("FCC_NO_SPINNER", raising=False)
    monkeypatch.setenv("TERM", "xterm")
    assert not spinner.animation_supported(_Stream(tty=False))


def test_animation_follows_no_spinner_and_term(monkeypatch):
    monkeypatch.setenv("TERM", "xterm")
    stream = _Stream(tty=True)
    assert spinner.animation_supported(stream)
    monkeypatch.setenv("FCC_NO_SPINNER", "1")
    assert not spinner.animation_supported(stream)
    monkeypatch.delenv("FCC_NO_SPINNER")
    monkeypatch.setenv("TERM", "dumb")
    assert not spinner.animation_supported(stream)


def test_disabled_spinner_draws_nothing(monkeypatch):
    monkeypatch.setenv("TERM", "xterm")
    stream = _Stream(tty=False)
    with spinner.StartupSpinner("Starting...", stream=stream) as active:
        assert not active.enabled
    assert stream.getvalue() == ""
