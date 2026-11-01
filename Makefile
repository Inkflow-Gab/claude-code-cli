.PHONY: help ubuntu-setup setup install preview-install verify check check-online run doctor

.DEFAULT_GOAL := help

# uv installs command wrappers into a user bin directory. Include it for make
# recipes immediately, without requiring the user to restart their shell.
export PATH := $(if $(UV_TOOL_BIN_DIR),$(UV_TOOL_BIN_DIR):)$(if $(XDG_BIN_HOME),$(XDG_BIN_HOME):)$(HOME)/.local/bin:$(HOME)/.cargo/bin:$(PATH)

# Leave AGENT empty for the interactive installer; set it for a one-agent setup.
AGENT ?=
export AGENT

help:
	@printf '%s\n' \
	  'Ubuntu quick start (run in this repository):' \
	  '  make setup AGENT=codex            Install Ubuntu prerequisites, FCC, and Codex' \
	  '  make ubuntu-setup                 Install system prerequisites (requires sudo)' \
	  '  make install AGENT=codex          Install FCC with one agent (claude, pi, etc.)' \
	  '  make install                      Choose coding agents interactively' \
	  '  make preview-install AGENT=codex  Show actions without changing anything' \
	  '  make verify                       Check installed FCC version' \
	  '  make check AGENT=codex            Check FCC and selected launcher' \
	  '  make check-online AGENT=codex     Also check the running local server' \
	  '  make run                          Start the server; keep this terminal open' \
	  '  make doctor                       Diagnose a running installation'

ubuntu-setup:
	@command -v apt-get >/dev/null || { echo 'ubuntu-setup requires Ubuntu/Debian with apt-get' >&2; exit 1; }
	sudo apt-get update
	sudo apt-get install -y ca-certificates curl git

setup: ubuntu-setup install

install:
	@if [ -z "$$AGENT" ] && [ ! -t 1 ]; then echo 'Non-interactive setup needs AGENT (example: make install AGENT=codex).' >&2; exit 2; fi
	@set --; if [ -n "$$AGENT" ]; then set -- --agent "$$AGENT"; fi; sh scripts/install.sh "$$@"

preview-install:
	@set --; if [ -n "$$AGENT" ]; then set -- --agent "$$AGENT"; fi; sh scripts/install.sh --dry-run "$$@"

verify:
	@command -v fcc-server >/dev/null || { echo 'fcc-server not found. Run make install AGENT=codex first.' >&2; exit 1; }
	@fcc-server --version

check:
	@set --; if [ -n "$$AGENT" ]; then set -- --agent "$$AGENT"; fi; sh scripts/check-setup.sh "$$@"

check-online:
	@set --; if [ -n "$$AGENT" ]; then set -- --agent "$$AGENT"; fi; sh scripts/check-setup.sh --online "$$@"

run:
	@command -v fcc-server >/dev/null || { echo 'fcc-server not found. Run make install AGENT=codex first.' >&2; exit 1; }
	fcc-server

doctor:
	@command -v fcc-doctor >/dev/null || { echo 'fcc-doctor not found. Run make install AGENT=codex first.' >&2; exit 1; }
	fcc-doctor
