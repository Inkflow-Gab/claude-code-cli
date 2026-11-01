# Use Free Claude Code from a phone

**Supported mobile setup:** FCC and the coding agent run on your own Ubuntu,
macOS, or Windows **computer**. Your Android or iPhone uses Telegram or Discord
to send requests; the agent edits files on the computer. You do **not** need to
install Python, Ubuntu, or FCC on the phone. Follow the
[computer installation guide](install-desktop.md) first.

**Not supported:** Running this project directly in Termux or proot Ubuntu on
Android. The pinned Python and some coding-agent binaries may be unavailable,
and Android may stop the server in the background. This guide does not claim
that a phone can host FCC natively.

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
