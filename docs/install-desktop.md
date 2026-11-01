# Install Nullx11 Code on a computer

Nullx11 Code uses Free Claude Code (FCC), which runs on your **computer** alongside a coding agent. It
routes the agent to a provider you configure; it does not supply Anthropic
credits or guarantee a free provider tier. Choose **one** installation path
below. Run commands one at a time, stopping if a step fails. Do not run the FCC
installer with `sudo`.

| Your computer | Start here |
| --- | --- |
| Ubuntu or Debian with a terminal | [Git + Make](#ubuntu-install) |
| macOS or another Linux distribution | [curl download](#macos-or-linux-curl-download) |
| Windows | [PowerShell](#windows-powershell) |
| Headless Ubuntu server | [Git + Make](#ubuntu-install), then [local Admin access](#start-fcc-and-open-admin) |

> **Android phone?** The [on-device Termux/proot experiment](install-mobile.md#run-on-the-android-phone-experimental)
> may fail due to pinned Python/agent binaries and Android background limits.
> Running FCC on a computer and using the phone as a remote control is the
> reliable path.

<a id="ubuntu-install"></a>

## Ubuntu or Debian: guided all-in-one path (recommended)

Install prerequisites, then clone the repository. Run each block separately:

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y ca-certificates curl git
```

```bash
git clone https://github.com/Inkflow-Gab/claude-code-cli.git
```

```bash
cd claude-code-cli
```

If this is an older clone, check for local changes and confirm the branch:

```bash
git status --short
```

```bash
git branch --show-current
```

```bash
git remote get-url origin
```

Only pull if the remote points to `Inkflow-Gab/claude-code-cli`, the checkout is
clean, and the branch is `main`. Otherwise use the fresh-installer fallback in
the README without altering your checkout. Refresh without discarding work:

```bash
git pull --ff-only origin main
```

Stop if that fails; do not force-reset local changes. For a diverged or dirty
checkout, follow the [fresh-installer fallback in the main README](../README.md#linux-ubuntu--debian)
instead of running its old script. Confirm the updated script lists `--guided`:

```bash
sh scripts/install.sh --help
```

Then install:

```bash
sh scripts/install.sh --guided
```

Choose one agent; the installer shows live steps, installs and verifies the
core and agent, then offers to start `fcc-server`. If you accept, leave that
terminal open and finish provider/key and model setup in the local Admin UI
(normally `http://127.0.0.1:8082/admin`). Open a second terminal and run
`nullx` from any directory, then select your coding agent. For scripts or
headless use, pass `--guided --agent codex`: this never starts a server
without a terminal. Only use `--from-checkout` when intentionally testing
local, unmerged source rather than the latest GitHub `main`.

## Ubuntu or Debian: Git + Make (alternative)

1. Refresh your package list:

   ```bash
   sudo apt-get update
   ```

2. Install Git, Make, and certificates:

   ```bash
   sudo apt-get install -y ca-certificates git make
   ```

3. Clone the repository:

   ```bash
   git clone https://github.com/Inkflow-Gab/claude-code-cli.git
   ```

4. Enter its directory:

   ```bash
   cd claude-code-cli
   ```

5. Optional: preview the installer without downloading or changing anything:

   ```bash
   make preview-install AGENT=codex
   ```

6. Install Ubuntu prerequisites (including curl), FCC, and **one** agent:

   ```bash
   make setup AGENT=codex
   ```

   Only the Ubuntu package installation asks for `sudo`; FCC installs for your
   user account. Choose `AGENT=claude`, `AGENT=pi`, etc. if you prefer another
   [supported agent](agents.md). Use the **same agent** in later checks. If
   prerequisites are already installed, `make install AGENT=codex` skips apt.
   Plain `make install` opens an interactive agent menu; in non-interactive
   terminals, specify `AGENT` to avoid installing the default full set.

7. Check the installed commands (no AI request is made):

   ```bash
   make check AGENT=codex
   ```

## macOS or Linux: curl download

Install `curl` first if it is missing. On Ubuntu/Debian:

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y ca-certificates curl
```

Download the installer to a file so you can review it. **Continue only if
curl succeeds.** If the download fails, delete the incomplete file before
retrying; never run a stale copy by accident.

```bash
curl -fL --progress-bar -o fcc-install.sh "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.sh"
```

Install FCC and choose one agent, then optionally start the server and Admin:

```bash
sh fcc-install.sh --guided
```

For automation, pass `--guided --agent codex` instead (no server is started).

The installer shows actual download progress when run in a terminal. Open a
new terminal to pick up your updated PATH, then check the version:

```bash
fcc-server --version
```

This installer uses `uv` to install **this fork's GitHub `main`** version of
the `free-claude-code` package, not an unrelated published build. A downloaded
installer cannot use `--from-checkout`; the checked-out script can. Use
`sh fcc-install.sh --help` for additional options such as local voice support.

## Windows: PowerShell

In PowerShell, review [the installer](../scripts/install.ps1), then run:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.ps1")))
```

Choose at least one coding agent when prompted. Open a new PowerShell window
and check the installation:

```powershell
fcc-server --version
```

## Start FCC and open Admin

On Ubuntu, from the cloned repository:

```bash
make run
```

With a curl installation on Linux/macOS, start it with:

```bash
fcc-server
```

On macOS or Windows you can also open the Free Claude Code app. Keep the
server running. The log prints the **local** Admin URL, normally
`http://127.0.0.1:8082/admin`. Open it **on the same computer**, not via its LAN
IP. Never expose Admin or forward port 8082 to the public internet.

On a headless server, run this on a **trusted computer** with SSH access to
the Ubuntu host:

```bash
ssh -L 18082:127.0.0.1:8082 user@your-ubuntu-host
```

Keep that SSH session open and visit `http://127.0.0.1:18082/admin` on the trusted
computer. The tunnel still makes Admin appear local to FCC; do not publish it.

To check a running server from another terminal in the clone:

```bash
make check-online AGENT=codex
```

If you changed the server's `PORT`, set `FCC_PORT` to that same value for the
check. The check probes only local `/health`: it does **not** validate a key,
model, or external provider.

## Configure a provider and try an agent

1. Obtain credentials for a [provider](providers.md) you are
   permitted to use. For example, obtain a key from
   [NVIDIA NIM](https://build.nvidia.com/settings/api-keys).
2. In local Admin, enter `NVIDIA_NIM_API_KEY` (or your chosen provider's
   setting), select a tool-capable `MODEL`, then click **Apply**. Do not put
   keys in shell history, screenshots or issues.
3. Open a **second terminal** inside a real project directory and run the
   launcher for the agent you installed. For Codex:

   ```bash
   fcc-codex
   ```

   For Claude Code instead:

   ```bash
   fcc-claude
   ```

The server must stay running while you use the agent. See [all launchers](agents.md)
and [editor integrations](../README.md#connect-your-client).

## Troubleshooting

| Problem | First check |
| --- | --- |
| `curl`, `git`, or `make` is missing | On Ubuntu run the prerequisite apt steps above. |
| `fcc-server` not found | Open a new shell, or from the clone use `make check AGENT=codex` (Make includes uv's user bin directory). |
| Installer refuses an update | Stop all FCC server and client processes before reinstalling. |
| Local server doesn't respond | Keep `fcc-server`/`make run` running; confirm the port in the server log. |
| Agent has no model response | Check the selected model and provider credentials in Admin; a local health check alone cannot test your provider. |
| Upstream download fails | Check your network and the upstream installer error; binaries may not exist for every CPU/OS. |

After installing, `fcc-doctor` prints diagnostics and may copy them to your
clipboard. Review the report before sharing it. See [the mobile guide](install-mobile.md)
if you want to control the host from a phone.
