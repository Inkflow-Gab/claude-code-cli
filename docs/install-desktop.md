# Install Free Claude Code on a computer

Free Claude Code (FCC) runs on your **computer** alongside a coding agent. It
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

> **Android phone with Termux/proot Ubuntu?** On-device installation is not
> supported: pinned Python and some agent binaries may not be available for
> Android/ARM, and Android may stop background processes. To use FCC *from* a
> phone, [run it on a computer and use the mobile guide](install-mobile.md).

<a id="ubuntu-install"></a>

## Ubuntu or Debian: Git + Make (recommended)

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

Install FCC and one agent (replace `codex` if desired):

```bash
sh fcc-install.sh --agent codex
```

The installer shows actual download progress when run in a terminal. Open a
new terminal to pick up your updated PATH, then check the version:

```bash
fcc-server --version
```

This installer uses `uv` to install the **published** `free-claude-code`
package, not the Git checkout as an editable Python package. Use
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
