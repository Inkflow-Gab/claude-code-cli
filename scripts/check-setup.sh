#!/bin/sh
# Read-only installation and optional local server check. Never reads API keys.
set -eu

agent=""
port="${FCC_PORT:-8082}"
online=0

usage() {
    cat <<'USAGE'
Usage: check-setup.sh [--agent NAME] [--online] [--port NUMBER]

Checks the installed Free Claude Code command and optionally a selected agent.
--online also checks the local /health endpoint; start fcc-server first.
Does not read credentials, make provider requests, or modify configuration.
USAGE
}

fail() { printf 'FAIL: %s\n' "$1" >&2; exit 1; }

while [ "$#" -gt 0 ]; do
    case "$1" in
        --agent|--port)
            option=$1
            shift
            [ "$#" -gt 0 ] || fail "$option needs a value"
            if [ "$option" = --agent ]; then
                [ -n "$1" ] || fail "--agent needs a value"
                agent=$1
            else
                port=$1
            fi
            ;;
        --agent=*) agent=${1#*=}; [ -n "$agent" ] || fail "--agent needs a value" ;;
        --port=*) port=${1#*=} ;;
        --online) online=1 ;;
        --help|-h) usage; exit 0 ;;
        *) fail "unknown option $1 (see --help)" ;;
    esac
    shift
done

case "$agent" in
    ''|claude|codex|pi|opencode|cline|hermes|dsh|grok|muse|aider) ;;
    *) fail "unknown agent: $agent" ;;
esac
case "$port" in
    ''|*[!0-9]*) fail "port must be a number from 1 to 65535" ;;
esac
[ "$port" -ge 1 ] && [ "$port" -le 65535 ] || fail "port must be a number from 1 to 65535"

command -v fcc-server >/dev/null 2>&1 || fail "fcc-server not found; install FCC first (make setup AGENT=codex)"
version=$(fcc-server --version 2>&1) || fail "fcc-server --version failed"
printf 'PASS: %s\n' "$version"

if [ -n "$agent" ]; then
    command -v "fcc-$agent" >/dev/null 2>&1 || fail "fcc-$agent not found; rerun the installer with --agent $agent"
    printf 'PASS: fcc-%s is on PATH\n' "$agent"
fi

if [ "$online" -eq 1 ]; then
    command -v curl >/dev/null 2>&1 || fail "curl is required to check the server"
    # Loopback-only request, with proxies disabled and a short timeout. No auth
    # header, provider key, or configuration is sent to another host.
    response=$(curl --noproxy '*' --max-time 3 -fsS "http://127.0.0.1:$port/health") ||
        fail "server is not responding on 127.0.0.1:$port; start fcc-server or pass --port"
    [ "$response" = '{"status":"healthy"}' ] ||
        fail "unexpected health response on port $port; check which service is listening"
    printf 'PASS: FCC is responding on 127.0.0.1:%s\n' "$port"
fi

printf 'Next: configure a provider in the local Admin UI and try your coding agent.\n'
