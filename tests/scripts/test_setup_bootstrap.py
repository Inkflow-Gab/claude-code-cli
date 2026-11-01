"""A stale checkout can run current main without overwriting local Git work."""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts" / "setup.sh"
INSTALLER = ROOT / "scripts" / "install.sh"


def _run_bootstrap(tmp_path: Path, source: Path | None, *args: str):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    curl = bin_dir / "curl"
    curl.write_text(
        '#!/bin/sh\nwhile [ "$#" -gt 0 ]; do\n'
        '  if [ "$1" = -o ]; then shift; destination=$1; fi\n'
        "  shift\ndone\n"
        '[ -n "${SOURCE_INSTALLER:-}" ] || exit 22\n'
        'cp "$SOURCE_INSTALLER" "$destination"\n',
        encoding="utf-8",
    )
    curl.chmod(0o755)
    elsewhere = tmp_path / "unrelated-directory"
    elsewhere.mkdir(exist_ok=True)
    return subprocess.run(
        ["sh", str(BOOTSTRAP), *args],
        cwd=elsewhere,
        env={
            **os.environ,
            "PATH": f"{bin_dir}:{os.environ['PATH']}",
            "TMPDIR": str(tmp_path),
            "SOURCE_INSTALLER": str(source) if source else "",
        },
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )


def test_bootstrap_runs_current_guided_installer_from_any_directory(tmp_path: Path):
    result = _run_bootstrap(tmp_path, INSTALLER, "--dry-run", "--agent", "codex")
    assert result.returncode == 0, result.stderr
    assert "Installer verified" in result.stdout
    assert "Ensuring Codex is installed" in result.stdout
    assert "Dry run complete. No changes were made." in result.stdout
    assert not list(tmp_path.glob("nullx-installer.*"))


def test_bootstrap_refuses_old_or_invalid_installer(tmp_path: Path):
    old = tmp_path / "old.sh"
    old.write_text("#!/bin/sh\necho should-not-run\n", encoding="utf-8")
    result = _run_bootstrap(tmp_path, old, "--dry-run", "--agent", "codex")
    assert result.returncode != 0
    assert "does not support --guided" in result.stderr
    assert "should-not-run" not in result.stdout
    assert not list(tmp_path.glob("nullx-installer.*"))


def test_bootstrap_preserves_installer_failure_status(tmp_path: Path):
    failing = tmp_path / "failing.sh"
    failing.write_text("#!/bin/sh\n# --guided)\nexit 7\n", encoding="utf-8")
    result = _run_bootstrap(tmp_path, failing, "--agent", "codex")
    assert result.returncode == 7
    assert not list(tmp_path.glob("nullx-installer.*"))


def test_bootstrap_refuses_download_failure_and_checkout_option(tmp_path: Path):
    result = _run_bootstrap(tmp_path, None, "--agent", "codex")
    assert result.returncode != 0
    assert "Download failed" in result.stderr
    result = _run_bootstrap(tmp_path, INSTALLER, "--from-checkout")
    assert result.returncode != 0
    assert "requires the checked-out" in result.stderr
    assert not list(tmp_path.glob("nullx-installer.*"))
