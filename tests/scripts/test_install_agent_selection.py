"""Dry-run coverage for the small Ubuntu installation path."""

import os
import shlex
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INSTALLER = ROOT / "scripts" / "install.sh"


def run_installer(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", str(INSTALLER), *args],
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_codex_only_dry_run() -> None:
    result = run_installer("--agent=codex", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "Ensuring Codex is installed" in result.stdout
    assert "Ensuring Claude Code is installed" not in result.stdout
    assert "Ensuring Grok Build is installed" not in result.stdout
    assert "Dry run complete. No changes were made." in result.stdout


def test_guided_dry_run_is_one_agent_and_does_not_start_server() -> None:
    result = run_installer("--guided", "--dry-run", "--agent", "codex")
    assert result.returncode == 0, result.stderr
    assert "Ensuring Codex is installed" in result.stdout
    assert "Ensuring Claude Code is installed" not in result.stdout
    assert "Installation steps completed" in result.stdout
    assert "Starting the local server" not in result.stdout
    assert "Dry run complete. No changes were made." in result.stdout


def test_guided_interactive_selects_only_codex() -> None:
    if os.name == "nt" or shutil.which("script") is None:
        return
    command = f"sh {shlex.quote(str(INSTALLER))} --guided --dry-run"
    result = subprocess.run(
        ["script", "-q", "-e", "-c", command, "/dev/null"],
        input="\n",
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Selected: codex" in result.stdout
    assert "Ensuring Codex is installed" in result.stdout
    assert "Ensuring Claude Code is installed" not in result.stdout
    assert "Dry run complete. No changes were made." in result.stdout


def test_guided_handoff_starts_only_on_confirmation(tmp_path: Path) -> None:
    if os.name == "nt" or shutil.which("script") is None:
        return
    text = INSTALLER.read_text(encoding="utf-8")
    helper = text.split("start_guided_server() {", 1)[1].split("\nquote_arg() {", 1)[0]
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    marker = tmp_path / "started"
    server = bin_dir / "fcc-server"
    server.write_text(
        f"#!/bin/sh\nprintf started > {shlex.quote(str(marker))}\n", encoding="utf-8"
    )
    server.chmod(0o755)
    fixture = tmp_path / "handoff.sh"
    fixture.write_text(
        'guided=1; dry_run=0; tool_bin="$1"\n'
        "installer_is_interactive() { :; }\n"
        'prompt_yes_no() { IFS= read -r reply <&3; [ "$reply" = y ]; }\n'
        'fail() { printf "%s\\n" "$*" >&2; exit 1; }\n'
        "start_guided_server() {" + helper + "\nstart_guided_server\n",
        encoding="utf-8",
    )
    command = f"sh {shlex.quote(str(fixture))} {shlex.quote(str(bin_dir))}"
    for answer, expected in (("n\n", False), ("y\n", True)):
        marker.unlink(missing_ok=True)
        result = subprocess.run(
            ["script", "-q", "-e", "-c", command, "/dev/null"],
            input=answer,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert marker.exists() is expected


def test_guided_noninteractive_requires_explicit_agent() -> None:
    result = run_installer("--guided")
    assert result.returncode != 0
    assert "needs a terminal to choose an agent" in result.stderr
    assert "Installing or updating Free Claude Code" not in result.stdout


def test_guided_checkout_source_resolves_outside_repo(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            "sh",
            str(INSTALLER),
            "--guided",
            "--dry-run",
            "--agent",
            "codex",
            "--from-checkout",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert f"--python 3.14.7 {ROOT}" in result.stdout
    assert (
        "git+https://github.com/Inkflow-Gab/claude-code-cli.git@main"
        not in result.stdout
    )


def test_claude_only_dry_run() -> None:
    result = run_installer("--dry-run", "--agent", "claude")
    assert result.returncode == 0, result.stderr
    assert "Ensuring Claude Code is installed" in result.stdout
    assert "Ensuring Codex is installed" not in result.stdout


def test_invalid_agent_fails_before_installation() -> None:
    for args in (("--agent=",), ("--agent=unknown",), ("--agent",), ("--agent", "")):
        result = run_installer(*args)
        assert result.returncode != 0
        assert "error:" in result.stderr
        assert "Installing or updating Free Claude Code" not in result.stdout


def test_curl_download_helper_preserves_success_and_failure(tmp_path: Path) -> None:
    if shutil.which("curl") is None:
        return
    text = INSTALLER.read_text(encoding="utf-8")
    # Run the real helper in isolation, without invoking any upstream installers.
    helper = text.split("download_file() {", 1)[1].split("\ndownload_and_run() {", 1)[0]
    command = (
        "print_command() { :; }\ndownload_file() {"
        + helper
        + '\ndownload_file "$1" "$2" fixture\n'
    )
    source = tmp_path / "sample.sh"
    source.write_text("echo safe\n", encoding="utf-8")
    destination = tmp_path / "download.sh"
    result = subprocess.run(
        ["sh", "-c", command, "sh", source.as_uri(), str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert destination.read_bytes() == source.read_bytes()
    assert "\x1b[" not in result.stdout + result.stderr

    result = subprocess.run(
        ["sh", "-c", command, "sh", (tmp_path / "missing").as_uri(), str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0


def test_download_progress_blends_blue_only_on_a_tty(tmp_path: Path) -> None:
    if os.name == "nt" or shutil.which("curl") is None:
        return
    import pty

    text = INSTALLER.read_text(encoding="utf-8")
    helper = text.split("download_file() {", 1)[1].split("\ndownload_and_run() {", 1)[0]
    command = (
        "print_command() { :; }\ndownload_file() {"
        + helper
        + '\ndownload_file "$1" "$2" fixture\n'
    )
    source = tmp_path / "input.sh"
    source.write_text("echo hello\n", encoding="utf-8")
    for no_color in (False, True):
        master, slave = pty.openpty()
        env = {**os.environ, "TERM": "xterm-256color"}
        if no_color:
            env["NO_COLOR"] = ""
        else:
            env.pop("NO_COLOR", None)
        try:
            result = subprocess.run(
                ["sh", "-c", command, "sh", source.as_uri(), str(tmp_path / "out.sh")],
                stdout=subprocess.PIPE,
                stderr=slave,
                env=env,
                check=False,
            )
            os.close(slave)
            slave = -1
            chunks = []
            while True:
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
            output = b"".join(chunks)
            assert result.returncode == 0
            if no_color:
                assert b"\x1b[" not in output
            else:
                assert b"38;5;45m" in output
                assert b"38;5;111m" in output
                assert b"38;5;91m" not in output
                assert b"\x1b[0m" in output
        finally:
            if slave != -1:
                os.close(slave)
            os.close(master)


def test_make_install_without_agent_fails_when_non_interactive() -> None:
    if shutil.which("make") is None:
        return
    result = subprocess.run(
        ["make", "-f", str(ROOT / "Makefile"), "install"],
        cwd=ROOT,
        env={**os.environ, "AGENT": ""},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "needs AGENT" in result.stderr


def test_make_verify_finds_user_install(tmp_path: Path) -> None:
    if shutil.which("make") is None:
        return
    bin_dir = tmp_path / ".local" / "bin"
    bin_dir.mkdir(parents=True)
    server = bin_dir / "fcc-server"
    server.write_text(
        '#!/bin/sh\nprintf "free-claude-code test\\n"\n', encoding="utf-8"
    )
    server.chmod(0o755)
    env = {**os.environ, "HOME": str(tmp_path)}
    env.pop("UV_TOOL_BIN_DIR", None)
    env.pop("XDG_BIN_HOME", None)
    result = subprocess.run(
        ["make", "-f", str(ROOT / "Makefile"), "verify"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "free-claude-code test" in result.stdout
