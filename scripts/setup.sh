#!/bin/sh
# Fetch the current official installer, even when this checkout is stale.
# Does not modify or reset the user's Git working tree.
set -eu

INSTALLER_URL="https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.sh"
temporary_installer=""

cleanup() {
    if [ -n "$temporary_installer" ]; then
        rm -f "$temporary_installer"
    fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' HUP TERM

fail() {
    printf 'setup: %s\n' "$1" >&2
    exit 1
}

for argument in "$@"; do
    case "$argument" in
        --from-checkout)
            fail "--from-checkout requires the checked-out scripts/install.sh; this bootstrap downloads main."
            ;;
    esac
done

command -v curl >/dev/null 2>&1 || fail "curl is required. On Ubuntu, run: apt-get install -y ca-certificates curl"
command -v mktemp >/dev/null 2>&1 || fail "mktemp is required."
temporary_installer=$(mktemp "${TMPDIR:-/tmp}/nullx-installer.XXXXXXXX") || fail "Could not create a temporary installer."
printf 'Fetching the current Nullx11 Code installer from GitHub main...\n'
if ! curl -fL --retry 3 --retry-delay 1 --connect-timeout 15 --max-time 90 \
    "$INSTALLER_URL" -o "$temporary_installer"; then
    fail "Download failed. Check network access and retry; no installer was run."
fi
[ -s "$temporary_installer" ] || fail "Downloaded installer is empty; nothing was run."
sh -n "$temporary_installer" || fail "Downloaded installer has invalid shell syntax; nothing was run."
grep -q -- '--guided)' "$temporary_installer" ||
    fail "Downloaded installer does not support --guided; nothing was run."

printf 'Installer verified. Starting guided setup from GitHub main.\n'
# Run as a child so the EXIT trap removes the temporary file afterward.
# Preserve the real exit status for users and automation.
sh "$temporary_installer" --guided "$@"
