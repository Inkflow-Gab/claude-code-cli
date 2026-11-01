# Install or use Nullx11 Code on a phone

Choose **one** mode: experimental [Android on-device](#run-on-the-android-phone-experimental)
installation, or [remote control](#phone-as-a-remote-control) of a computer.
An iPhone cannot run this project locally; use remote control instead.

## Run on the Android phone (experimental)

**Not officially supported or tested on Android.** This may fail on your device:
FCC pins Python 3.14.7 and requires dependencies and a coding-agent binary that
may not have working ARM64/proot builds. This path installs **Ubuntu under
Termux**, not native Android Python. Use a 64-bit device with enough free
storage and memory. Stop at the first error; do not run installer commands
with Android root permissions.

Open the [official Termux app](https://termux.dev/) and enter each command
separately in **Termux**:

```sh
uname -m
```

Check for `aarch64` (32-bit ARM builds are not expected to work).

```sh
pkg update
```

```sh
pkg install proot-distro
```

```sh
proot-distro install ubuntu
```

```sh
proot-distro login ubuntu
```

The prompt is now Ubuntu inside proot. Run the following **inside Ubuntu**;
proot commonly presents a simulated root user, so use `apt-get` without `sudo`:

```sh
apt-get update
```

```sh
apt-get install -y ca-certificates curl git make
```

```sh
git clone https://github.com/Inkflow-Gab/claude-code-cli.git
```

```sh
cd claude-code-cli
```

If you cloned this repo previously (including before the guided installer was
merged), **do not re-clone over it**. In the existing `~/claude-code-cli`
checkout inside Ubuntu, check for local edits:

```sh
git status --short
```

```sh
git branch --show-current
```

```sh
git remote get-url origin
```

The remote must be `https://github.com/Inkflow-Gab/claude-code-cli.git`
(or its SSH equivalent), not an upstream or unrelated fork. If it is different,
use the fresh-installer fallback below instead of pulling from that remote.
If there are no local edits and the branch output is `main`, update it safely.
If it is blank, this may be a detached checkout from older instructions:
`git switch main` is appropriate only after preserving your work. If it names
another branch, stop rather than accidentally updating the wrong branch.

```sh
git pull --ff-only origin main
```

If the pull refuses because of local changes or a diverged branch, stop and
preserve those changes instead of force-resetting. Confirm that the *local*
script now supports the option:

```sh
sh scripts/install.sh --help
```

Look for `--guided` in the output. Merely updating the installed FCC package
will not update scripts in an older checkout. If the pull cannot safely
fast-forward, **leave your checkout untouched** and download the current
installer to your home directory instead:

```sh
curl -fL --retry 3 -o "$HOME/nullx-main-install.sh" "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.sh"
```

Run the next steps **only if curl succeeded**:

```sh
sh -n "$HOME/nullx-main-install.sh"
```

```sh
grep -q -- '--guided)' "$HOME/nullx-main-install.sh"
```

```sh
sh "$HOME/nullx-main-install.sh" --guided --agent codex
```

Do not then run the old `scripts/install.sh` from your clone; it is still old.
This is an experimental on-device install: proot may lack compatible Python
or coding-agent ARM64 builds. For an updated checkout, preview the single-agent
install without network changes:

```sh
sh scripts/install.sh --dry-run --agent codex
```

If the preview succeeds, try the install. This downloads Python, FCC, and an
upstream Codex installer; success depends on their ARM64 support:

```sh
sh scripts/install.sh --guided --agent codex
```

When asked to start the server, answer **n** here: the commands below start it
explicitly on loopback. The phone's browser may not open automatically from
inside proot.

```sh
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

```sh
sh scripts/check-setup.sh --agent codex
```

Start FCC on **loopback only** (keep Termux open):

```sh
HOST=127.0.0.1 fcc-server
```

Open `http://127.0.0.1:8082/admin` in the **same phone's browser**. Add a
[provider](providers.md) key or account and select a model in Admin. Open a
**second Termux session** and enter Ubuntu again:

```sh
proot-distro login ubuntu
```

In that second Ubuntu shell, go back to your checkout:

```sh
cd claude-code-cli
```

```sh
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

```sh
fcc-codex
```

Try a small prompt. FCC edits files **inside this phone's Ubuntu environment**.
To reopen the environment later, run `proot-distro login ubuntu` in Termux,
then restart FCC; closing Termux or Android background restrictions can kill
it. Running `make setup` inside proot is **not** the recommended path: it uses
`sudo` for system packages, which proot Ubuntu may not have. Use the explicit
`apt-get` and `sh scripts/install.sh` commands above.

**If installation fails:** Do not assume it will work by forcing incompatible
wheels, downgrading Python, or switching to native Termux. Note the first
upstream error (Python download, package wheel, or Codex binary); these are
platform limitations, not a bot configuration issue. Use the
[computer install](install-desktop.md) and remote mode below instead. Local
Whisper and GPU/CUDA installation are not recommended in proot.

## Phone as a remote control

This is the **reliable option**: FCC and the agent run on a separate Ubuntu,
macOS, or Windows computer. Android or iPhone uses Telegram/Discord. Install on
the [computer first](install-desktop.md); the phone needs no Python or Ubuntu.

```text
Phone app -> Telegram or Discord -> FCC server on your computer -> coding agent
                                                        -> files on your computer
```

## Before you start

- Install FCC and one agent on the computer, and select a provider in its
  [local Admin UI](install-desktop.md#configure-a-provider-and-try-an-agent).
- Start `fcc-server` (or `make run` from the Ubuntu checkout) and leave it
  running. The phone needs network access to Telegram/Discord; the computer
  needs access to those services and your provider.
- Choose **one** platform below. Telegram is simplest for a private chat.
- Pick a real project directory on the computer, for example
  `/home/you/projects/myapp`. Do not select your entire home directory.

Admin is **local-only**: opening the host's LAN IP in a phone browser will not
work. Configure the bot in Admin on the computer itself. For a headless host,
use the [SSH tunnel instructions](install-desktop.md#start-fcc-and-open-admin)
from a trusted computer. Do not expose port 8082 or Admin to the internet.

## Option A: Telegram (recommended)

1. On your phone, open [@BotFather](https://t.me/BotFather) in Telegram and
   send `/newbot`. Follow its prompts to create a bot and copy its **token**.
   Keep the token secret; anyone with it can control your bot.
2. Send `/start` to [@userinfobot](https://t.me/userinfobot) and copy the
   numeric **user ID** it replies with (not your Telegram username).
3. On the computer, open FCC's local Admin URL from the server log. In
   **Messaging**, enter:

   | Setting | Value |
   | --- | --- |
   | Messaging Platform | `telegram` |
   | Telegram Bot Token | Your BotFather token |
   | Allowed Telegram User ID | Your numeric user ID |
   | Allowed Directory | Absolute path to one project on the computer |

4. Click **Apply** and restart `fcc-server` if requested. On your phone, open
   your new bot's chat and tap **Start** before sending a request. Send a small
   test prompt such as “List the files in this project.” Results appear in the
   same chat.

## Option B: Discord

1. Open the [Discord Developer Portal](https://discord.com/developers/applications),
   create an application, open **Bot**, reset/copy its token, and turn on
   **Message Content Intent** under **Privileged Gateway Intents**.
2. Under **OAuth2 → URL Generator**, select the `bot` scope and grant **View
   Channels**, **Send Messages**, **Read Message History**, and **Manage
   Messages** (for `/clear`). Open the generated invitation URL to add the bot
   to a server you administer. Do not put the token in the invite URL.
3. In Discord, enable **User Settings → Advanced → Developer Mode**. Right-click
   the channel the bot can see and choose **Copy Channel ID**.
4. On the computer, open local FCC Admin → **Messaging** and enter:

   | Setting | Value |
   | --- | --- |
   | Messaging Platform | `discord` |
   | Discord Bot Token | Your Developer Portal token |
   | Allowed Discord Channels | The channel ID you copied |
   | Allowed Directory | Absolute path to one project on the computer |

5. Click **Apply** and restart the FCC server if requested. Message the bot in
   the permitted channel with a small test prompt. Check its channel permissions
   and Message Content Intent if it connects but ignores messages.

## Commands and voice notes

| Chat command | Effect |
| --- | --- |
| `/stats` | Show session state. |
| `/stop` | Cancel work in this chat. Reply with `/stop` to cancel only that request. |
| `/clear` | Clear history in this chat. Reply with `/clear` to clear only that message chain. |

For optional voice-note transcription, configure `NVIDIA_NIM_API_KEY` in Admin,
then enable **Messaging → Voice**, select `nvidia_nim`, and pick a supported
model. This uses your provider's quota. Local Whisper requires extra packages:
stop FCC and re-run the installer with `--voice-local` and the **same agent**
you installed before. On an Ubuntu Git checkout, for Codex:

```bash
sh scripts/install.sh --agent codex --voice-local
```

Restart the server, then choose `cpu` in **Messaging → Voice**. Local voice may
require substantial memory; CUDA users can consult [the installer options](../README.md#optional-integrations).

## If your bot does not reply

1. Check that the computer still has a running FCC server and internet access.
   Turning the phone screen off does not stop a server on the computer.
2. Check the bot token and the **exact allowed user ID or channel ID** in Admin.
   Telegram bots cannot message you first: tap **Start** in your bot's chat.
3. For Discord, check Message Content Intent and the bot's channel permissions.
4. Confirm a provider and tool-capable model are selected in Admin. On the host,
   run `fcc-doctor` for diagnostics (review the report before sharing).
5. If Telegram/Discord throttles requests, lower **Messaging Rate Limit** and
   raise **Messaging Rate Window** in Admin → Messaging.

## Security

Bot tokens are credentials. FCC stores managed settings in `~/.fcc/.env`; keep
that file private. Only give access to your own Telegram ID or the necessary
Discord channel, and use a narrow project directory. Anyone who can message an
allowed bot can run an agent that executes code on your computer. Revoke a
leaked token through [@BotFather](https://t.me/BotFather) (`/revoke`) or the
[Discord Developer Portal](https://discord.com/developers/applications).
