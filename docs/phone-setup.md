# Use Free Claude Code From Your Phone

Control your coding agent from Telegram or Discord. Your phone becomes the
keyboard and screen; the agent still runs on your own computer and edits your
real files.

```
  Your phone                Telegram / Discord              Your computer
  "fix the login bug"  ────────────────>   fcc-server  ──>  Claude Code / Codex
                             <──────────────── results  <──   (edits real files)
```

Telegram is the easier default. This guide uses an **Ubuntu computer or server**
as the host; Android or iPhone only needs the Telegram/Discord app. It does not
install FCC on the phone.

---

## What you need

- An Ubuntu computer with FCC installed, a working coding agent, and a provider
  key configured (see [Ubuntu quick start](../README.md#ubuntu-and-phone-setup))
- A Telegram or Discord account
- This guide

---

## Step 0. Install FCC on Ubuntu (skip if already installed)

For Ubuntu, use the [copyable `git clone` and `make setup AGENT=codex` steps](../README.md#ubuntu-and-phone-setup),
or use the [curl download method](../README.md#install) if you do not want to
clone. The installer runs on the Ubuntu host, **not** the phone. Termux/proot
Ubuntu on Android is not supported: the pinned Python and agent binaries may
not be available there.

For macOS/Linux, use the same [curl download method](../README.md#install).

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.ps1")))
```

The Ubuntu and curl examples install Codex by default; change `AGENT=codex`
(or `--agent codex`) if you prefer another coding agent. Messaging works with
any supported agent. The Windows installer prompts you to select one.

Check it installed:

```bash
fcc-server --version
```

---

## Step 1. Start FCC

Run this on your computer and **leave the terminal open**:

```bash
fcc-server
```

Your phone is only a remote control. If this stops, the bot stops responding.
Open Admin on the Ubuntu machine using the URL in the log (normally
`http://127.0.0.1:8082/admin`). Admin is local-only: a phone browser pointed
at the Ubuntu machine's IP will not be allowed in. Configure it on the host,
then use Telegram or Discord from the phone. Do not open/forward port 8082 to
the internet.

---

## Step 2. Create a bot (choose Telegram **or** Discord)

Telegram is simplest for a private chat. If you choose Telegram, do Step 2a
and use Option A in Step 4; for Discord, use Step 2b and Option B instead.

### Step 2a. Telegram

Copy this command into your Telegram chat with [@BotFather](https://t.me/BotFather):

```
/newbot
```

Follow the prompts to name it and pick a username. BotFather replies with a
token that looks like this:

```
7123456789:AAHexampleTokenYourBotTokenHere_x1y2z3
```

Copy that token. You need it in Step 4.

> **Treat the token like a password.** Anyone holding it controls your bot. Never
> paste it into a chat, a screenshot, or a public issue.

---

### Step 2b. Discord

1. Open the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**, name it, and click **Create**
3. Open **Bot** in the sidebar, then click **Reset Token**
4. Copy the token that appears

Now turn on the permission the bot needs:

5. Open **Privileged Gateway Intents**
6. Enable **MESSAGE CONTENT INTENT**

If you skip this step the bot connects but ignores everything you send.

7. Open **OAuth2 → URL Generator** in the Developer Portal, select the `bot`
   scope, and grant **View Channels**, **Send Messages**, **Read Message History**,
   and **Manage Messages** (needed for `/clear`). Open the generated URL and
   invite the bot to a server you administer. Ensure it can see the channel you
   will allow in Step 4. Never paste the bot token into the invite URL.

---

## Step 3. Find your user or channel ID

### Telegram

Send this to [@userinfobot](https://t.me/userinfobot):

```
/start
```

It replies with your numeric ID, for example `123456789`. That number is what
FCC uses to recognise you.

### Discord

1. Open **User Settings → Advanced → Developer Mode** and turn it on
2. Right-click your own name anywhere in Discord
3. Choose **Copy User ID**

For a specific channel instead, right-click the channel and choose
**Copy Channel ID**. You will need the bot's ID too: open **User Settings →
Advanced → Developer Mode**, then open your bot's profile.

---

## Step 4. Configure it

Start `fcc-server`, open the Admin UI (it prints the URL on startup), then go to
**Messaging**.

Fill in one of these two blocks.

### Option A: Telegram

| Field | Value |
| --- | --- |
| Messaging Platform | `telegram` |
| Telegram Bot Token | The token from BotFather |
| Allowed Telegram User ID | Your numeric ID |
| Allowed Directory | An absolute path, e.g. `/home/you/projects/myapp` |

### Option B: Discord

| Field | Value |
| --- | --- |
| Messaging Platform | `discord` |
| Discord Bot Token | The token from the Developer Portal |
| Allowed Discord Channels | The channel ID, e.g. `1234567890123456789` |
| Allowed Directory | An absolute path, e.g. `/home/you/projects/myapp` |

> **Set Allowed Directory to a real project folder, not your home directory.**
> This is the boundary that keeps the agent inside your code.

Click **Apply**, then restart `fcc-server` when prompted.

---

## Step 5. Message your bot

Open Telegram or Discord on your phone and send a message to your bot.

```
fix the failing test in parser.py
```

Results stream back into the same chat.

---

## Commands

| Command | What it does |
| --- | --- |
| `/stats` | Show session state |
| `/stop` | Cancel all work |
| `/clear` | Clear this chat's history |

**Reply** to a specific message to scope either command to just that one:

- Reply `/stop` to a message to cancel only that request and leave the rest of
  your queue running
- Reply `/clear` to delete that message and the replies under it, keeping the
  rest of the conversation

This is the difference between a runaway job and everything else waiting behind
it. Use reply-scoped `/stop` first.

---

## Voice notes

Talk instead of typing. Send a voice message and it gets transcribed, then the
agent works on it.

### Option A: NVIDIA NIM (already included, easiest)

1. Get a key from [build.nvidia.com](https://build.nvidia.com/settings/api-keys)
2. In Admin, set `NVIDIA_NIM_API_KEY`
3. Go to **Messaging → Voice**, enable voice notes, set device to `nvidia_nim`,
   and pick a model

### Option B: Local Whisper on your own machine

Stop `fcc-server` first. From your cloned repository, re-run the installer
with local voice support (change `codex` if you installed a different agent):

```bash
sh scripts/install.sh --agent codex --voice-local
```

For an NVIDIA GPU on Ubuntu:

```bash
sh scripts/install.sh --agent codex --voice-local --torch-backend cu130
```

If you used curl instead of Git, run these commands against the downloaded
`fcc-install.sh` file instead of `scripts/install.sh`.

Then restart `fcc-server`, and in **Messaging → Voice** choose `cpu` or `cuda`.

Windows PowerShell, local voice:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.ps1"))) -VoiceLocal
```

---

## Troubleshooting

**The bot does not reply**
Confirm `fcc-server` is still running. Then check that your user ID in
**Messaging** matches your real ID — this is the most common cause.

**Telegram: "Forbidden: bot was blocked"**
The bot cannot message you first. Open the bot's chat and tap **Start** once.

**Discord: the bot ignores every message**
**MESSAGE CONTENT INTENT** is off. Turn it on in the Developer Portal, then
restart the bot.

**Nothing happens, no error**
The bot is receiving your message but the agent cannot run. Check
**Messaging** settings, the selected coding agent, and your provider key, then run the diagnostic:

```bash
fcc-doctor
```

**`fcc-server: command not found` on Ubuntu**
Open a new terminal, or run `export PATH="$HOME/.local/bin:$PATH"` and retry.
The installer verifies that `fcc-server` is installed before it exits.

**The bot stops answering when the phone screen turns off**
FCC must keep running on the Ubuntu host, not on the phone. Check the Ubuntu
terminal and network connection; don't close the terminal running `fcc-server`.

**Rate limits or "FloodWait" errors**
Telegram and Discord both throttle. FCC pauses automatically, but if you hit
limits often, lower **Messaging Rate Limit** and raise **Messaging Rate Window**
in **Messaging**.

---

## Security notes

- Bot tokens are stored in `~/.fcc/.env`, which FCC keeps at `0600` permissions
- Only the user ID or channel ID you allow can drive the agent
- **Allowed Directory** bounds which files the agent can touch
- Anyone who can message your bot can run code on your machine. Keep the allowed
  user list to just yourself
- Revoke a leaked bot token in [@BotFather](https://t.me/BotFather) with
  `/revoke`, or in the [Discord Developer Portal](https://discord.com/developers/applications)

---

## See also

- [Main README](../README.md) for provider setup
- [Provider setup](../README.md#choose-a-provider) and [integrations](../README.md#optional-integrations)
