"""Dry-run coverage for the small Ubuntu installation path."""

import os
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

    result = subprocess.run(
        ["sh", "-c", command, "sh", (tmp_path / "missing").as_uri(), str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0


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
