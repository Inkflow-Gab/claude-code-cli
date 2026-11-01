"""Interactive Nullx11 Code front door for existing FCC workflows."""

import json
import os
import re
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from free_claude_code.core.version import package_version

REPOSITORY = "Inkflow-Gab/claude-code-cli"
AGENTS = (
    "claude",
    "codex",
    "pi",
    "opencode",
    "cline",
    "hermes",
    "dsh",
    "grok",
    "muse",
    "aider",
)


def _choose(prompt: str, options: tuple[str, ...]) -> int | None:
    print(f"\n{prompt}")
    for index, label in enumerate(options, 1):
        print(f"  {index}. {label}")
    while True:
        try:
            answer = input("Choose a number (or q to exit): ").strip().lower()
        except EOFError, KeyboardInterrupt:
            print()
            return None
        if answer in {"q", "quit", "exit"}:
            return None
        if answer.isascii() and answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        print("Enter one of the listed numbers, or q.")


def _installed_revision() -> str | None:
    # Hatch-vcs local versions contain a Git revision. Source checkouts can use
    # HEAD; PyPI versions with no Git identity cannot safely be compared to main.
    match = re.search(r"\+[^\s]*g([0-9a-f]{7,40})(?:\.|$)", package_version())
    if match:
        return match.group(1)
    root = Path(__file__).resolve().parents[3]
    if (root / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
        except OSError, subprocess.TimeoutExpired:
            return None
        if result.returncode == 0 and re.fullmatch(
            r"[0-9a-f]{40}", result.stdout.strip()
        ):
            return result.stdout.strip()
    return None


def _github_json(path: str) -> dict[str, object]:
    request = Request(
        f"https://api.github.com/repos/{REPOSITORY}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "nullx-update-check",
        },
    )
    with urlopen(request, timeout=4) as response:
        return json.load(response)


def _check_update() -> str | None:
    revision = _installed_revision()
    if revision is None:
        return None
    try:
        comparison = _github_json(f"compare/{revision}...main")
        ahead_by = comparison.get("ahead_by")
        if (
            comparison.get("status") != "ahead"
            or not isinstance(ahead_by, int)
            or ahead_by <= 0
        ):
            return None
        commit = _github_json("commits/main").get("sha")
        return (
            commit
            if isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{40}", commit)
            else None
        )
    except (HTTPError, URLError, OSError, TimeoutError, ValueError, KeyError) as exc:
        print(
            f"Update check unavailable ({exc}). Continuing without updating.",
            file=sys.stderr,
        )
        return None


def _offer_update() -> None:
    revision = _check_update()
    if revision is None:
        return
    print(f"New code is available on GitHub main ({revision[:12]}).")
    if input("Install this revision with uv now? [y/N] ").strip().lower() not in {
        "y",
        "yes",
    }:
        return
    uv = _command_path("uv")
    if uv is None:
        print("uv is required for updating. Install uv, then try nullx again.")
        return
    print(
        "Stop any running FCC server before updating. Your configuration is not modified."
    )
    if input("Proceed with installation? [y/N] ").strip().lower() not in {"y", "yes"}:
        return
    spec = f"free-claude-code @ git+https://github.com/{REPOSITORY}.git@{revision}"
    result = subprocess.run(
        [uv, "tool", "install", "--force", "--python", "3.14.7", spec], check=False
    )
    if result.returncode:
        print(
            "Update failed; existing setup may still be available. See uv output above.",
            file=sys.stderr,
        )
    else:
        print("Update installed. Restart nullx to use the new version.")
        raise SystemExit(0)


def _command_path(command: str) -> str | None:
    """Resolve companion entry points without relying on the current directory.

    uv's command directory may not yet be in PATH in the installing terminal.
    Sibling scripts in that directory (or this tool's venv) still work.
    """
    found = shutil.which(command)
    if found:
        return found
    for directory in (Path(sys.argv[0]).resolve().parent, Path(sys.executable).parent):
        for name in (command, f"{command}.exe", f"{command}.cmd"):
            candidate = directory / name
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
    return None


def _run(command: str, *, env: dict[str, str] | None = None) -> None:
    path = _command_path(command)
    if path is None:
        print(f"{command} is not installed. Run the installer first.", file=sys.stderr)
        return
    try:
        result = subprocess.run([path], env=env, check=False)
    except KeyboardInterrupt:
        print()
        return
    if result.returncode:
        print(f"{command} exited with status {result.returncode}.", file=sys.stderr)


def _messaging() -> None:
    platform = _choose("Connect from your phone or community", ("Telegram", "Discord"))
    if platform is None:
        return
    name, token = (
        ("telegram", "TELEGRAM_BOT_TOKEN"),
        ("discord", "DISCORD_BOT_TOKEN"),
    )[platform]
    # The server reads its normal managed config; the override is only for this
    # process, so choosing a different mode does not overwrite user settings.
    from free_claude_code.config.loader import get_settings
    from free_claude_code.config.server_urls import local_admin_url

    settings = get_settings()
    configured = getattr(settings, token.lower(), None)
    if not configured:
        url = f"{local_admin_url(settings)}/messaging"
        print(f"Configure {name.title()} bot credentials in Admin first: {url}")
        print(
            "Start fcc-server in another terminal, save the bot token in Admin, then retry."
        )
        webbrowser.open(url)
        return
    print(f"Starting the existing {name.title()} workflow. Press Ctrl+C to stop.")
    _run("fcc-server", env={**os.environ, "MESSAGING_PLATFORM": name})


def _cli() -> None:
    choice = _choose(
        "Launch a coding agent through FCC", tuple(f"fcc-{agent}" for agent in AGENTS)
    )
    if choice is None:
        return
    print(
        "Ensure fcc-server is running in another terminal with a provider and model configured."
    )
    _run(f"fcc-{AGENTS[choice]}")


def main() -> None:
    """Show the menu; network checks and prompts only run in interactive mode."""
    if "--version" in sys.argv[1:]:
        print(f"Nullx11 Code (free-claude-code {package_version()})")
        return
    if "--help" in sys.argv[1:]:
        print(
            "Usage: nullx [--help | --version]\nInteractive menu for messaging and FCC coding agents."
        )
        return
    if len(sys.argv) > 1:
        raise SystemExit("Unknown option. Use nullx --help.")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise SystemExit(
            "nullx needs an interactive terminal. Use fcc-server or fcc-* directly in scripts."
        )
    print("Nullx11 Code  /  local control")
    try:
        _offer_update()
        while True:
            choice = _choose(
                "Where would you like to work?",
                (
                    "Telegram or Discord",
                    "Coding agent CLI",
                    "Open local web dashboard",
                    "Start FCC server",
                ),
            )
            if choice is None:
                return
            if choice == 0:
                _messaging()
            elif choice == 1:
                _cli()
            elif choice == 2:
                from free_claude_code.config.loader import get_settings
                from free_claude_code.config.server_urls import local_admin_url

                url = f"{local_admin_url(get_settings())}/welcome"
                print(f"Opening {url} (start fcc-server first if it is not running).")
                webbrowser.open(url)
            else:
                _run("fcc-server")
    except EOFError, KeyboardInterrupt:
        print("\nGoodbye.")
