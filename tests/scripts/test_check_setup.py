"""The setup check is read-only, loopback-only, and works without Python 3.14."""

import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check-setup.sh"


def run_check(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    server = bin_dir / "fcc-server"
    server.write_text('#!/bin/sh\necho "free-claude-code test"\n', encoding="utf-8")
    server.chmod(0o755)
    codex = bin_dir / "fcc-codex"
    codex.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    codex.chmod(0o755)
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}"}
    env.pop("FCC_PORT", None)
    return subprocess.run(
        ["sh", str(SCRIPT), *args],
        env=env,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )


def test_offline_check_does_not_need_server(tmp_path: Path) -> None:
    result = run_check(tmp_path, "--agent", "codex")
    assert result.returncode == 0, result.stderr
    assert "PASS: fcc-codex" in result.stdout


def test_online_check_requires_real_health(tmp_path: Path) -> None:
    result = run_check(tmp_path, "--agent", "codex", "--online", "--port", "1")
    assert result.returncode != 0
    assert "server is not responding" in result.stderr


def test_online_check_accepts_only_fcc_health(tmp_path: Path) -> None:
    class Health(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = b'{"status":"healthy"}' if self.path == "/health" else b"not found"
            self.send_response(200 if self.path == "/health" else 404)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_args: object) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Health)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        result = run_check(tmp_path, "--online", "--port", str(server.server_port))
        assert result.returncode == 0, result.stderr
        assert "PASS: FCC is responding" in result.stdout
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_rejects_invalid_arguments(tmp_path: Path) -> None:
    invalid = (
        ("--port", "abc"),
        ("--port", "65536"),
        ("--agent", "other"),
        ("--agent=",),
    )
    for args in invalid:
        result = run_check(tmp_path, *args)
        assert result.returncode != 0
        assert "FAIL:" in result.stderr
