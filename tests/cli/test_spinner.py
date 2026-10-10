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
    with spinner.StartupAnimation("Starting...", stream=stream) as active:
        assert not active.enabled
    assert stream.getvalue() == ""


def test_rainbow_render_uses_ansi_color_and_spark(monkeypatch):
    import re

    monkeypatch.setenv("TERM", "xterm")
    monkeypatch.delenv("NO_COLOR", raising=False)
    active = spinner.StartupAnimation("Booting...", stream=_Stream(tty=True))
    assert active.color
    rendered = active._render(3)
    # Each character is wrapped in rotating ANSI color with a bright spark.
    assert re.sub(r"\033\[\d+m", "", rendered) == "Booting..."
    assert "\033[" in rendered
    assert "\033[97m" in rendered
    # The spark travels: a later frame colors a different character bright.
    assert active._render(1) != rendered


def test_no_color_turns_off_ansi_painting(monkeypatch):
    monkeypatch.setenv("TERM", "xterm")
    monkeypatch.setenv("NO_COLOR", "1")
    active = spinner.StartupAnimation("Booting...", stream=_Stream(tty=True))
    assert active.enabled
    assert not active.color
