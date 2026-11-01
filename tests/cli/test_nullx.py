"""The Nullx11 menu does not install anything without explicit consent."""

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from free_claude_code.cli import nullx


def test_update_check_only_offers_when_main_is_ahead_of_installed_revision() -> None:
    sha = "a" * 40
    with (
        patch.object(nullx, "_installed_revision", return_value="b" * 40),
        patch.object(
            nullx,
            "_github_json",
            side_effect=[{"status": "ahead", "ahead_by": 1}, {"sha": sha}],
        ) as get,
    ):
        assert nullx._check_update() == sha
        assert get.call_count == 2
    with (
        patch.object(nullx, "_installed_revision", return_value="b" * 40),
        patch.object(
            nullx, "_github_json", return_value={"status": "identical", "ahead_by": 0}
        ),
    ):
        assert nullx._check_update() is None


def test_declining_update_never_runs_installer() -> None:
    with (
        patch.object(nullx, "_check_update", return_value="a" * 40),
        patch("builtins.input", return_value="n"),
        patch.object(nullx.subprocess, "run") as run,
    ):
        nullx._offer_update()
        run.assert_not_called()


def test_update_uses_pinned_commit_after_two_confirmations() -> None:
    sha = "a" * 40
    with (
        patch.object(nullx, "_check_update", return_value=sha),
        patch("builtins.input", side_effect=["yes", "yes"]),
        patch.object(nullx, "_command_path", return_value="/bin/uv"),
        patch.object(
            nullx.subprocess, "run", return_value=SimpleNamespace(returncode=1)
        ) as run,
    ):
        nullx._offer_update()
    run.assert_called_once_with(
        [
            "/bin/uv",
            "tool",
            "install",
            "--force",
            "--python",
            "3.14.7",
            f"free-claude-code @ git+https://github.com/{nullx.REPOSITORY}.git@{sha}",
        ],
        check=False,
    )


def test_menu_dispatches_existing_fcc_commands() -> None:
    with (
        patch.object(nullx, "_choose", return_value=1),
        patch.object(nullx, "_run") as run,
    ):
        nullx._cli()
    run.assert_called_once_with("fcc-codex")


def test_companion_command_resolves_from_any_directory(
    tmp_path: Path, monkeypatch
) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    command = bin_dir / "fcc-server"
    command.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    command.chmod(0o755)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    with (
        patch.object(nullx.sys, "argv", [str(bin_dir / "nullx")]),
        patch.object(nullx.shutil, "which", return_value=None),
    ):
        assert nullx._command_path("fcc-server") == str(command)


def test_messaging_uses_only_child_process_override() -> None:
    from free_claude_code.config import loader

    original_platform = os.environ.get("MESSAGING_PLATFORM")
    with (
        patch.object(nullx, "_choose", return_value=0),
        patch.object(
            loader,
            "get_settings",
            return_value=SimpleNamespace(telegram_bot_token="test-token"),
        ),
        patch.object(nullx, "_run") as run,
    ):
        nullx._messaging()
    run.assert_called_once()
    assert run.call_args.args == ("fcc-server",)
    assert run.call_args.kwargs["env"]["MESSAGING_PLATFORM"] == "telegram"
    assert os.environ.get("MESSAGING_PLATFORM") == original_platform


def test_version_is_available_from_an_unrelated_directory(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    with (
        patch.object(nullx.sys, "argv", ["/somewhere/bin/nullx", "--version"]),
        patch.object(nullx, "package_version", return_value="1.2.3"),
        patch.object(nullx, "_check_update") as check,
    ):
        nullx.main()
    assert "1.2.3" in capsys.readouterr().out
    check.assert_not_called()


def test_noninteractive_does_not_call_network() -> None:
    with (
        patch.object(nullx.sys, "argv", ["nullx"]),
        patch.object(nullx.sys.stdin, "isatty", return_value=False),
        patch.object(nullx, "_check_update") as check,
    ):
        try:
            nullx.main()
        except SystemExit as exc:
            assert "interactive" in str(exc)
        else:
            raise AssertionError("Expected non-interactive exit")
        check.assert_not_called()
