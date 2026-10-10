"""Non-blocking startup animation for interactive terminals.

The animation is cosmetic only: it never raises, never blocks the startup
path, and disables itself permanently on the first output error. It is skipped
whenever the stream is not an interactive terminal so piped output, CI logs, and
``fcc-server --version`` stay byte-for-byte unchanged.
"""

import os
import sys
import threading
from typing import TextIO

_UNICODE_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
_ASCII_FRAMES = "|/-\\"
_INTERVAL_SECONDS = 0.08
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


class StartupSpinner:
    """Animate a single status line until the server is ready.

    Used as a context manager so the animation is always torn down::

        with StartupSpinner("Starting Free Claude Code"):
            server.run()
    """

    def __init__(
        self,
        message: str,
        *,
        stream: TextIO | None = None,
        interval: float = _INTERVAL_SECONDS,
    ) -> None:
        self._message = message
        self._stream = sys.stderr if stream is None else stream
        self._interval = max(0.02, float(interval))
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._enabled = animation_supported(self._stream)
        self._frames = _UNICODE_FRAMES
        self._painted = False
        # Bounds the join in stop() and guarantees the painter always exits.
        self._stopped = threading.Event()

    @property
    def enabled(self) -> bool:
        """Report whether the animation is actually painting."""

        return self._enabled

    def start(self) -> None:
        """Begin animating. Safe to call when already running."""

        if not self._enabled or self._thread is not None:
            return
        self._stopped.clear()
        thread = threading.Thread(
            target=self._run, name="fcc-startup-spinner", daemon=True
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
        index = 0
        while not self._stopped.is_set():
            self._paint(self._frames[index % len(self._frames)])
            index += 1
            if self._stopped.wait(self._interval):
                return

    def _paint(self, frame: str) -> None:
        with self._lock:
            if not self._enabled:
                return
            try:
                self._stream.write(f"\r{frame} {self._message}")
                self._stream.flush()
            except UnicodeEncodeError:
                # Legacy Windows consoles frequently cannot encode braille.
                self._frames = _ASCII_FRAMES
                try:
                    self._stream.write(f"\r{_ASCII_FRAMES[0]} {self._message}")
                    self._stream.flush()
                except Exception:
                    self._enabled = False
                    return
            except Exception:
                self._enabled = False
                return
            self._painted = True

    def _width(self) -> int:
        return len(f"  {self._message}")

    def __enter__(self) -> StartupSpinner:
        self.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self.stop()
