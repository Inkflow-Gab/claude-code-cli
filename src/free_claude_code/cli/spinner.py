"""Non-blocking, colorful startup animation for interactive terminals.

The animation is cosmetic only: it never raises, never blocks the startup
path, and disables itself permanently on the first output error. It is skipped
whenever the stream is not an interactive terminal so piped output, CI logs, and
``fcc-server --version`` stay byte-for-byte unchanged.

While running, the status message shimmers in a rainbow palette whose colors
rotate every frame, with a bright spark sweeping back and forth through the
text. No spinner glyph, progress line, circle, or box is used: the animation is
pure colored text. When ``NO_COLOR`` is set the animation degrades to a plain
blinking marker so the terminal never sees undecodable escape sequences.
"""

import os
import sys
import threading
from typing import TextIO

_ANSI_RESET = "\033[0m"
_ANSI_BRIGHT = "\033[97m"
_ANSI_RAINBOW = (
    "\033[91m",  # bright red
    "\033[93m",  # bright yellow
    "\033[92m",  # bright green
    "\033[96m",  # bright cyan
    "\033[94m",  # bright blue
    "\033[95m",  # bright magenta
)
_MAX_WIDTH = 48
_INTERVAL_SECONDS = 0.06
_TRUTHY = frozenset({"1", "true", "yes", "on"})


def animation_supported(stream: TextIO | None = None) -> bool:
    """Report whether an animation can be drawn on ``stream``."""

    if os.environ.get("FCC_NO_SPINNER", "").strip().lower() in _TRUTHY:
        return False
    target = sys.stderr if stream is None else stream
    try:
        if not target.isatty():
            return False
    except Exception:
        return False
    return os.environ.get("TERM", "").lower() != "dumb"


def color_supported() -> bool:
    """Report whether the terminal is expected to render ANSI color."""

    if os.environ.get("NO_COLOR", "").strip():
        return False
    if os.name == "nt":
        # Windows 10+ consoles enable virtual terminal processing by default.
        return True
    term = os.environ.get("TERM", "").lower()
    return bool(term) and term != "dumb"


class StartupAnimation:
    """Animate a single status line until the server is ready.

    Used as a context manager so the animation is always torn down::

        with StartupAnimation("Starting Free Claude Code"):
            server.run()
    """

    def __init__(
        self,
        message: str,
        *,
        stream: TextIO | None = None,
        interval: float = _INTERVAL_SECONDS,
    ) -> None:
        self._text = message[:_MAX_WIDTH]
        self._stream = sys.stderr if stream is None else stream
        self._interval = max(0.02, float(interval))
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._enabled = animation_supported(self._stream)
        self._color = self._enabled and color_supported()
        self._painted = False
        # Bounds the join in stop() and guarantees the painter always exits.
        self._stopped = threading.Event()

    @property
    def enabled(self) -> bool:
        """Report whether the animation is actually painting."""

        return self._enabled

    @property
    def color(self) -> bool:
        """Report whether the animation paints with ANSI color."""

        return self._color

    def start(self) -> None:
        """Begin animating. Safe to call when already running."""

        if not self._enabled or self._thread is not None:
            return
        self._stopped.clear()
        thread = threading.Thread(
            target=self._run, name="fcc-startup-animation", daemon=True
        )
        self._thread = thread
        try:
            thread.start()
        except Exception:
            self._enabled = False
            self._thread = None

    def stop(self, message: str | None = None) -> None:
        """Stop animating, optionally leaving a final ``message`` line."""

        thread = self._thread
        self._stopped.set()
        if thread is not None:
            self._thread = None
            # The painter checks the flag between frames, so this join is short.
            thread.join(timeout=self._interval * 8)
        self._write_final(message)

    def _render(self, frame: int) -> str:
        """Color the message: rotating rainbow plus a traveling bright spark."""

        text = self._text
        length = len(text)
        hue = frame % len(_ANSI_RAINBOW)
        spark = self._spark_position(frame, length)
        parts: list[str] = []
        for index, ch in enumerate(text):
            if index == spark:
                parts.append(_ANSI_BRIGHT)
            else:
                parts.append(_ANSI_RAINBOW[(hue + index) % len(_ANSI_RAINBOW)])
            parts.append(ch)
        parts.append(_ANSI_RESET)
        return "".join(parts)

    @staticmethod
    def _spark_position(frame: int, length: int) -> int:
        """Frame -> character index, ping-ponging across the text."""

        if length < 1:
            return 0
        span = 2 * length
        travel = frame % span
        if travel < length:
            return travel
        return span - 1 - travel

    def _write_final(self, message: str | None) -> None:
        if not self._enabled:
            return
        with self._lock:
            painted = self._painted
            self._painted = False
            try:
                if painted:
                    self._stream.write("\r" + " " * self._width() + "\r")
                if message:
                    self._stream.write(message + "\n")
                self._stream.flush()
            except Exception:
                self._enabled = False

    def _run(self) -> None:
        frame = 0
        while not self._stopped.is_set():
            self._paint(frame)
            frame += 1
            if self._stopped.wait(self._interval):
                return

    def _paint(self, frame: int) -> None:
        with self._lock:
            if not self._enabled:
                return
            try:
                if self._color:
                    self._stream.write("\r" + self._render(frame))
                else:
                    marker = "*" if frame % 2 == 0 else " "
                    self._stream.write(f"\r{marker} {self._text}")
                self._stream.flush()
            except Exception:
                self._enabled = False
                return
            self._painted = True

    def _width(self) -> int:
        # ANSI escapes are invisible; only the text characters need clearing.
        return len(self._text) + (0 if self._color else 2)

    def __enter__(self) -> StartupAnimation:
        self.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self.stop()


# Backwards-compatible alias for code that referenced the old name.
StartupSpinner = StartupAnimation