<div align="center">

<h1>
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/free-claude-code-wordmark-light.svg">
    <img src="assets/free-claude-code-wordmark-dark.svg" alt="Free Claude Code" width="610">
  </picture>
</h1>

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-2e7d32.svg?style=for-the-badge)](https://github.com/Inkflow-Gab/claude-code-cli/blob/main/LICENSE)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776ab.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Package Manager: uv](assets/package-manager-uv.svg)](https://github.com/astral-sh/uv)
[![Testing: Pytest](https://img.shields.io/badge/Testing-Pytest-ad1457.svg?style=for-the-badge)](https://github.com/Inkflow-Gab/claude-code-cli/actions/workflows/tests.yml)
[![Type Checker: Ty](https://img.shields.io/badge/Type%20Checker-ty-fdd835.svg?style=for-the-badge)](https://pypi.org/project/ty/)
[![Formatter: Ruff](https://img.shields.io/badge/Formatter-ruff-bf4b00.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Logging: Loguru](https://img.shields.io/badge/logging-loguru-00695c.svg?style=for-the-badge)](https://github.com/Delgan/loguru)

[Start here](#quick-start) · [Ubuntu & phone](#ubuntu-and-phone-setup) · [Agents](docs/agents.md) · [Providers](#choose-a-provider) · [Integrations](#optional-integrations) · [Help](#troubleshooting)

</div>

<p align="center">
  <em>Independent open-source project. Not affiliated with or endorsed by Anthropic. Claude and Claude Code are trademarks of Anthropic.</em>
</p>

> **Attribution:** This is a maintained copy of **Free Claude Code** by
> [Alishahryar1](https://github.com/Alishahryar1). The original project lives at
> [github.com/Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code),
> and its installer remains at
> `https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.sh`.
> See [Credits](#credits) below.

## Free Claude Code at a glance

Free Claude Code (FCC) runs a **local proxy** between coding agents and model
providers. Choose a coding agent, configure a provider you have access to, and
use the `fcc-*` launchers to route requests through FCC. Provider free tiers
and quotas are controlled by their operators; FCC does not grant free Claude
Code or Anthropic credits. You may need a provider API key or subscription.

- Run [Claude Code, Codex, Pi and other agents](docs/agents.md) with a shared
  model catalog. FCC also supports browser Code Sessions and client integrations.
- Choose among [hosted, subscription and local providers](#choose-a-provider),
  with optional fallback models. Check each provider's current terms and limits.
- Code from an Ubuntu host or [control it from your phone](docs/phone-setup.md)
  using Telegram or Discord. The server and project files remain on the host.
- Optional voice notes, desktop integrations and RTK are documented below.

## Quick Start

Choose **one** path. Run commands on the computer hosting FCC, not on the phone.
Do not run the installer with `sudo`: only the Ubuntu package prerequisites
need elevated privileges. [Review the shell installer](scripts/install.sh) before
running downloaded code.

<a id="install"></a>

### 1. Install

**Ubuntu with Git + Make (recommended).** Run each command separately,
in order, on the Ubuntu host. Wait for one to finish successfully before
copying the next; do not paste the whole section at once.

1. Refresh Ubuntu's package list:

   ```bash
   sudo apt-get update
   ```

2. Install the tools needed to get the project:

   ```bash
   sudo apt-get install -y ca-certificates git make
   ```

3. Clone this repository:

   ```bash
   git clone https://github.com/Inkflow-Gab/claude-code-cli.git
   ```

4. Enter the repository:

   ```bash
   cd claude-code-cli
   ```

5. Optionally preview the installation without making changes:

   ```bash
   make preview-install AGENT=codex
   ```

6. Install curl, Free Claude Code, and Codex. This step asks for `sudo` only
   for Ubuntu packages. **Do not run Make or the FCC installer with `sudo`.**

   ```bash
   make setup AGENT=codex
   ```

7. Verify the installed FCC and selected agent commands:

   ```bash
   make check AGENT=codex
   ```

Change `codex` in steps 5–7 to the same other agent (`claude`, `pi`, etc.)
if you prefer. See `sh scripts/install.sh --help` for names. `make install
AGENT=codex` skips Ubuntu packages if curl is already installed. `make install`
without an agent opens the full selection menu **in an interactive terminal**;
non-interactive Make installs require `AGENT`. The Make commands add uv's user
bin directory to PATH without requiring a new terminal. Ubuntu running
*inside Android* (Termux/proot) is not supported: Python and agent binaries
may not be available.

**macOS/Linux using curl instead of Git.** On minimal Ubuntu, install curl first:

```bash
sudo apt-get update
```

```bash
sudo apt-get install -y ca-certificates curl
```

Download the installer and **continue only if curl succeeds**:

```bash
curl -fL --progress-bar -o fcc-install.sh "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.sh"
```

Review the file if you wish, then install FCC with one agent:

```bash
sh fcc-install.sh --agent codex
```

If the download failed, do **not** run an old or incomplete `fcc-install.sh`;
remove it and retry. `--agent` avoids the long selection menu (omit it to
choose interactively). The installer displays real download progress on a
terminal and installs the published `free-claude-code` package with uv, not an
editable Python checkout. Open a new terminal after installation, then verify:

```bash
fcc-server --version
```

**Windows PowerShell:**

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.ps1")))
```

### 2. Start the server

On Ubuntu/Linux, start FCC from the clone:

```bash
make run
```

If you installed with curl, or are on macOS, run:

```bash
fcc-server
```

On Windows/macOS you can also open the Free Claude Code app. Keep the server
terminal open. Admin is available **only on the host** at the URL
shown in its log (normally `http://127.0.0.1:8082/admin`). Do not expose Admin
to the internet. On a headless server, tunnel from a trusted computer with
`ssh -L 18082:127.0.0.1:8082 user@your-ubuntu-host`, then open
`http://127.0.0.1:18082/admin` on that computer.

From the clone, check the running server **in a second terminal**:

```bash
make check-online AGENT=codex
```

If you changed the server port, set `FCC_PORT` to that port when running the
check. This confirms the server responds; it does
**not** test a provider or make an AI request.

<a id="nvidia-nim-provider"></a>
<a id="3-configure-nvidia-nim"></a>

### 3. Configure NVIDIA NIM (example provider)

1. Get an API key at [build.nvidia.com](https://build.nvidia.com/settings/api-keys).
2. In local Admin, enter `NVIDIA_NIM_API_KEY`. Choose a model in the `MODEL`
   dropdown, such as `nvidia_nim/nvidia/nemotron-3-super-120b-a12b`.
3. Click **Apply**. For other providers, see [Choose a provider](#choose-a-provider).

Do not paste keys into terminal commands, public issues or screenshots. For
extra protection of the proxy API, enable **Proxy Authentication** in Admin.

### 4. Try an agent or your phone

Open another terminal on the host and start Codex (if you selected Codex):

```bash
fcc-codex
```

Or start Claude Code (if you selected Claude Code):

```bash
fcc-claude
```

Then try a prompt in a project directory. The server must be running.
Choose the same agent you installed in step 1. See [all launchers](docs/agents.md),
[client integrations](#connect-your-client), or the
[phone walkthrough](docs/phone-setup.md) for Telegram/Discord setup.

<a id="ubuntu-and-phone-setup"></a>

## Ubuntu and phone setup

For a phone, **keep FCC and your project on Ubuntu**. Install Telegram or Discord
on the phone, configure the bot in local Admin on Ubuntu, then message it from
the phone. No port forwarding or public Admin URL is required. Start with the
[phone guide](docs/phone-setup.md). A phone browser cannot open the Admin UI
by pointing it at the Ubuntu machine's LAN address; Admin is loopback-only.

## Troubleshooting

| Symptom | What to try |
| --- | --- |
| `curl` or `make` not found | Install prerequisites with `sudo apt-get update && sudo apt-get install -y ca-certificates curl git make`. |
| `fcc-server` not found after install | From the clone, use `make check AGENT=codex`; for direct commands, reopen the terminal or add `~/.local/bin` (or `UV_TOOL_BIN_DIR`) to PATH. |
| Installer refuses to update | Stop `fcc-server` and FCC clients; rerun `make install AGENT=codex`. |
| Server check fails | Start `make run` in another terminal. If you changed `PORT`, run `FCC_PORT=<port> make check-online AGENT=codex`. |
| Agent cannot get a response | Confirm the selected model and provider credentials in Admin; run `make doctor` after installing, or `fcc-doctor` outside the clone. |
| Package or agent download fails | Read the upstream error; retry when connected. Some architectures do not have compatible binaries. |

The checks never read credentials or call a model provider. For a bug report,
`fcc-doctor` prints a diagnostic report; review it before sharing.

## Choose A Provider

1. Open a provider link below for its key, models, or setup instructions.
2. In the Admin UI, configure the listed setting. For OpenAI / ChatGPT
   subscription access, use **Providers → OAuth providers** instead.
3. Search the `MODEL` dropdown and select a model. If the provider cannot list
   models, enter `<provider-id>/<exact-provider-model-id>` manually.
4. Click **Apply**.

Optional: add an ordered **Fallback Models** list under **Model Config**. It
applies to every connected client. A failed request may reach and consume usage
from more than one provider before succeeding.

For another API endpoint, open **Providers → Custom providers → Add provider**. Enter its API base URL, optional key, and API format. Leave **Model IDs** empty to discover models automatically, or enter one upstream model ID per line. Save, then select a model in **Model Config**.

<details>
<summary><strong>Provider catalog</strong></summary>

| Provider | Admin UI setting | Example `MODEL` |
| --- | --- | --- |
| [NVIDIA NIM](https://build.nvidia.com/settings/api-keys) | `NVIDIA_NIM_API_KEY` | `nvidia_nim/nvidia/nemotron-3-super-120b-a12b` |
| [OpenRouter](https://openrouter.ai/keys) | `OPENROUTER_API_KEY` | `open_router/openrouter/free` |
| [Groq](https://console.groq.com/keys) | `GROQ_API_KEY` | `groq/llama-3.3-70b-versatile` |
| [ClinePass](https://docs.cline.bot/getting-started/clinepass) | `CLINE_API_KEY` | `cline_pass/cline-pass/kimi-k3` |
| [OpenAI / ChatGPT](https://learn.chatgpt.com/docs/auth) | Connect ChatGPT in the Admin UI | `openai/<model-id>` |
| [OpenAI API](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` | `openai_api/gpt-5.6-sol` |
| [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-sdk/auth/authenticate) | Connect GitHub Copilot in the Admin UI | `github_copilot/<model-id>` |
| [xAI (Grok)](https://console.x.ai/team/default/api-keys) | `XAI_API_KEY` | `xai/grok-4.5` |
| [Alibaba Cloud](https://www.alibabacloud.com/help/en/model-studio/get-api-key) | `ALIBABA_CLOUD_API_KEY` | `alibaba_cloud/<model-id>` |
| [QwenCloud Token Plan](https://home.qwencloud.com/api-keys) | `QWENCLOUD_API_KEY` | `qwencloud/qwen3.7-plus` |
| [QwenCloud Coding Plan](https://home.qwencloud.com/api-keys) | `QWENCLOUD_CODING_API_KEY` | `qwencloud_coding/qwen3.7-plus` |
| [Together AI](https://api.together.ai/settings/api-keys) | `TOGETHER_API_KEY` | `together/zai-org/GLM-5.2` |
| [DeepInfra](https://deepinfra.com/dash/api_keys) | `DEEPINFRA_API_KEY` | `deepinfra/deepseek-ai/DeepSeek-V4-Flash` |
| [SiliconFlow](https://cloud.siliconflow.com/account/ak) | `SILICONFLOW_API_KEY` | `siliconflow/Qwen/Qwen3-32B` |
| [Nebius Token Factory](https://tokenfactory.nebius.com/project/api-keys) | `NEBIUS_API_KEY` | `nebius/Qwen/Qwen3-30B-A3B` |
| [Chutes](https://chutes.ai/docs/getting-started/authentication) | `CHUTES_API_KEY` | `chutes/Qwen/Qwen3-32B-TEE` |
| [Featherless AI](https://featherless.ai/account/api-keys) | `FEATHERLESS_API_KEY` | `featherless/Qwen/Qwen3-32B` |
| [Agnes AI](https://agnes-ai.com/) | `AGNES_API_KEY` | `agnes/agnes-2.0-flash` |
| [ZenMux](https://zenmux.ai/platform/pay-as-you-go) | `ZENMUX_API_KEY` | `zenmux/deepseek/deepseek-v4-flash-free` |
| [W&B Inference](https://wandb.ai/settings) | `WANDB_API_KEY` | `wandb/openai/gpt-oss-20b` |
| [Anthropic](https://platform.claude.com/settings/keys) | `ANTHROPIC_API_KEY` | `anthropic/<model-id>` |
| [Azure OpenAI](https://learn.microsoft.com/azure/foundry/openai/how-to/chatgpt) | `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_BASE_URL` | `azure_openai/<deployment-name>` |
| [Google AI Studio (Gemini)](https://aistudio.google.com/apikey) | `GEMINI_API_KEY` | `gemini/models/gemini-3.1-flash-lite` |
| [Google Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/start/openai) | `VERTEX_PROJECT_ID` + ADC | `vertex/google/gemini-3.5-flash` |
| [DeepSeek](https://platform.deepseek.com/api_keys) | `DEEPSEEK_API_KEY` | `deepseek/deepseek-chat` |
| [Mistral La Plateforme](https://console.mistral.ai/) | `MISTRAL_API_KEY` | `mistral/devstral-small-latest` |
| [Mistral Codestral](https://console.mistral.ai/) | `CODESTRAL_API_KEY` | `mistral_codestral/codestral-latest` |
| [OpenCode Zen](https://opencode.ai/auth) | `OPENCODE_API_KEY` | `opencode_zen/gpt-5.3-codex` |
| [OpenCode Go](https://opencode.ai/auth) | `OPENCODE_API_KEY` | `opencode_go/minimax-m2.7` |
| [Vercel AI Gateway](https://vercel.com/docs/ai-gateway/models-and-providers) | `AI_GATEWAY_API_KEY` | `vercel/openai/gpt-5.5` |
| [Amazon Bedrock](https://console.aws.amazon.com/bedrock/) | `AWS_BEARER_TOKEN_BEDROCK` | `bedrock/openai.gpt-oss-120b` |
| [Hugging Face Inference Providers](https://huggingface.co/settings/tokens) | `HUGGINGFACE_API_KEY` | `huggingface/Qwen/Qwen3-Coder-480B-A35B-Instruct:fastest` |
| [Cohere](https://dashboard.cohere.com/api-keys) | `COHERE_API_KEY` | `cohere/command-a-plus-05-2026` |
| [Wafer](https://wafer.ai/) | `WAFER_API_KEY` | `wafer/DeepSeek-V4-Pro` |
| [Kimi API](https://platform.moonshot.ai/console/api-keys) | `KIMI_API_KEY` | `kimi/kimi-k2.5` |
| [Kimi Code](https://www.kimi.com/code/console) | `KIMI_CODE_API_KEY` | `kimi_code/k3` |
| [MiniMax](https://platform.minimax.io/user-center/basic-information/interface-key) | `MINIMAX_API_KEY` | `minimax/MiniMax-M3` |
| [Cerebras Inference](https://cloud.cerebras.ai/) | `CEREBRAS_API_KEY` | `cerebras/gpt-oss-120b` |
| [SambaNova](https://cloud.sambanova.ai/apis) | `SAMBANOVA_API_KEY` | `sambanova/Meta-Llama-3.3-70B-Instruct` |
| [Kilo.ai](https://kilo.ai) | `KILO_API_KEY` | `kilo/kilo-auto/free` |
| [Fireworks AI](https://fireworks.ai/account/api-keys) | `FIREWORKS_API_KEY` | `fireworks/accounts/fireworks/models/llama-v3p3-70b-instruct` |
| [Novita AI](https://novita.ai/settings/key-management) | `NOVITA_API_KEY` | `novita/deepseek/deepseek-v4-flash-0731` |
| [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/) | `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` | `cloudflare/@cf/moonshotai/kimi-k2.6` |
| [Z.ai Coding Plan](https://z.ai/manage-apikey/apikey-list) | `ZAI_API_KEY` | `zai/glm-5.2` |
| [Z.ai API (pay as you go)](https://z.ai/manage-apikey/apikey-list) | `ZAI_API_KEY` | `zai_api/glm-4.7-flash` |
| [TokenRouter](https://www.tokenrouter.com/) | `TOKENROUTER_API_KEY` | `tokenrouter/moonshotai/kimi-k3-free` |
| [NaraRoute](https://router.bynara.id/) | `NARAROUTE_API_KEY` | `nararoute/kimi-k3-free` |
| [Poolside AI](https://platform.poolside.ai/) | `POOLSIDE_API_KEY` | `poolside/poolside/laguna-s-2.1` |
| [LLM7.io](https://dash.llm7.io/) | `LLM7_API_KEY` | `llm7/default` |
| [Scaleway](https://console.scaleway.com/iam/api-keys) | `SCW_SECRET_KEY` | `scaleway/deepseek/deepseek-v4-flash` |
| [Lightning AI](https://lightning.ai/) | `LIGHTNING_API_KEY` | `lightning/lightning-ai/Qwen3.8-27B` |
| [Experiential Labs](https://platform.experientiallabs.ai/) | `EXPLABS_API_KEY` | `experiential/union-alpha` |
| [Cheaper Inference](https://cheaperinference.com/signup) | `CHEAPER_INFERENCE_API_KEY` | `cheaperinference/gpt-5.4-mini` |
| [OrcaRouter](https://www.orcarouter.ai/) | `ORCAROUTER_API_KEY` | `orcarouter/deepseek/deepseek-v4-flash-free` |
| [xKiro](https://xkiro.com/) | `XKIRO_API_KEY` | `xkiro/qwen/qwen3.7-flash:free` |
| [Opper](https://platform.opper.ai/) | `OPPER_API_KEY` | `opper/claude-sonnet-4-6` |
| [Ollama Cloud](https://ollama.com/settings/keys) | `OLLAMA_API_KEY` | `ollama_cloud/qwen3-coder:480b` |
| [LM Studio](https://lmstudio.ai/) | `LM_STUDIO_BASE_URL` | `lmstudio/<model-id>` |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | `LLAMACPP_BASE_URL` | `llamacpp/<model-id>` |
| [Ollama](https://ollama.com/) | `OLLAMA_BASE_URL` | `ollama/<model-tag>` |

</details>

<details>
<summary><strong>Provider-specific setup</strong></summary>

- OpenAI / ChatGPT uses your ChatGPT subscription rather than an API key. Connect from
  **Providers → OAuth providers → OpenAI / ChatGPT → Connect** in the Admin UI
  and finish signing in through your browser. Restart an already-running agent after connecting.
- Anthropic uses a separately billed API key. Add it under
  **Providers → Cloud providers → Anthropic → Configure**, then choose a discovered
  model. Multi-workspace keys also require `ANTHROPIC_WORKSPACE_ID`.
  Messages requests use Anthropic's native tools and the client's thinking controls.
  FCC local web tools and prompt optimizations apply to other routes. Native requests
  can fall back only to other Anthropic models. Anthropic tool access and charges apply.
- OpenAI API uses a separate Platform API key. Enter it under
  **Providers → Cloud providers → OpenAI API → Configure**. The model list may
  include IDs that cannot handle coding requests. Choose a text-generation model.
- GitHub Copilot uses your signed-in GitHub account and subscription. Install
  [Copilot CLI 1.0.83](https://github.com/github/copilot-cli/releases/tag/v1.0.83)
  on PATH, then choose **Providers → OAuth providers → GitHub Copilot → Connect**.
  Finish signing in, then select a `github_copilot/<model-id>` from the model picker.
  Available models and quotas depend on your subscription and organization policies.
  Restart an already-running agent after connecting.
- Azure OpenAI uses the deployment names from your resource. Set
  `AZURE_OPENAI_BASE_URL` to its complete v1 endpoint, such as
  `https://YOUR-RESOURCE-NAME.openai.azure.com/openai/v1/`, and select a
  deployment that supports Chat Completions. Enter the deployment name as a
  custom model slug if it does not appear in the model dropdown.
- Mistral Codestral uses a separate key from Mistral La Plateforme.
- Kimi Code subscription keys use `kimi_code/`. Kimi API credit keys use
  `kimi/`. Kimi Code plans are for personal interactive coding-agent use under
  [Kimi's community guidelines](https://www.kimi.com/code/docs/en/kimi-code/community-guidelines.html).
- Alibaba Cloud uses a Model Studio pay-as-you-go key and defaults to Singapore.
  For another region or workspace, set `ALIBABA_CLOUD_BASE_URL` to its
  [OpenAI-compatible endpoint](https://www.alibabacloud.com/help/en/model-studio/base-url)
  ending in `/compatible-mode/v1`. The key and endpoint must use the same region.
- QwenCloud Coding Plan keys use `qwencloud_coding/`. QwenCloud Token Plan keys
  use `qwencloud/`. The keys and endpoints are not interchangeable. Coding Plan
  is for local, personal, interactive coding-agent use under the
  [Coding Plan terms](https://www.alibabacloud.com/help/en/model-studio/coding-plan).
- OpenCode Zen and OpenCode Go share `OPENCODE_API_KEY` but use the explicit
  `opencode_zen/` and `opencode_go/` model prefixes.
- For Amazon Bedrock, set `BEDROCK_BASE_URL` to the URL for the same region as
  the API key and select one of the listed models.
- Vertex AI uses Google Application Default Credentials instead of an API key.
  Locally, run `gcloud auth application-default login` once. Service-account
  files and attached service accounts also work. Set `VERTEX_PROJECT_ID`, and
  optionally change `VERTEX_LOCATION` from its `global` default.
- Cloudflare requires both its API token and account ID.
- For Ollama Cloud, use the exact model IDs shown in the model picker. Local
  Ollama uses the separate `ollama/` prefix.
- Prefer tool-capable models for coding agents. Local models also need enough context for the agent's system prompt and tool definitions.

</details>

<details>
<summary><strong>Local provider setup</strong></summary>

### LM Studio

Start LM Studio's local server, load a tool-capable model, and use the model identifier shown by LM Studio with the `lmstudio/` prefix. The default URL is `http://localhost:1234/v1`.

### llama.cpp

Start `llama-server` with its OpenAI-compatible Chat Completions API and enough context for the model. Use the local model ID with the `llamacpp/` prefix. `LLAMACPP_BASE_URL` defaults to `http://localhost:8080/v1`.

### Ollama

```bash
ollama pull llama3.1
```

Then, in another terminal:

```bash
ollama serve
```

Use the tag shown by `ollama list` with the `ollama/` prefix. `OLLAMA_BASE_URL` defaults to `http://localhost:11434`.

</details>

<details>
<summary><strong>Optional model-tier routing</strong></summary>

`MODEL` is the fallback for every request. Select a model for `MODEL_FABLE`, `MODEL_OPUS`, `MODEL_SONNET`, or `MODEL_HAIKU` to override an individual Claude Code tier. Select **None** to use `MODEL`.

</details>

<details>
<summary><strong>Reasoning control</strong></summary>

Open **Admin UI → Model Config → Reasoning** and select the behavior you want.

| Selection | Behavior |
| --- | --- |
| **From client** (default) | Use the effort sent by your coding agent. If none is sent, keep the provider default. |
| **Off** | Request reasoning to be disabled. |
| **Low**, **Medium**, **High**, **X-High**, or **Max** | Override the client with the selected reasoning level. |
| **Inherit** (Fable, Opus, Sonnet, and Haiku only) | Use the root Reasoning selection. |

Providers that do not support a selected control retain their own behavior.

</details>

<a id="connect-your-client"></a>

## Connect Your Client

For editor and app integrations, install the client, start FCC, then open
**Admin UI → Integrations** and click **Connect** on its card.

- **Claude Code in VS Code**: Install the [Claude Code extension](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code).
- **VS Code Chat**: Install the latest [VS Code](https://code.visualstudio.com/), connect, and select an FCC model in its built-in Chat model picker.
- **Claude Desktop**: Install [Claude Desktop](https://claude.ai/download). Fully quit it before connecting or disconnecting, then reopen it. Disconnect returns to normal Claude sign-in.
- **Codex in VS Code and App**: Install the [Codex extension](https://marketplace.visualstudio.com/items?itemName=openai.chatgpt) or Codex App.
- **Claude Code in JetBrains ACP**: Install Claude Agent in JetBrains AI Assistant and start it once, then click **Connect** in FCC. Reopen the IDE, select **Claude Code (FCC)**, and start a new chat. After JetBrains updates the agent, restart FCC before starting a new chat. Requires a local IDE in its standard installation locations.

Reload VS Code or restart the app/IDE after connecting. In Codex and Claude Desktop, select an FCC
model from the model picker. Reload or restart the client when FCC reports updated settings. Use
**Disconnect** on the same card to remove the integration.

Run FCC on the same computer and in the same user environment as the client you
are configuring.

<a id="optional-integrations"></a>

## Optional Integrations

Configure integrations from **Admin UI → Messaging**, then click **Apply**.

> **Driving FCC from your phone?** See [Use Free Claude Code From Your Phone](docs/phone-setup.md)
> for a step-by-step setup with copy-ready commands.

<details>
<summary><strong>Discord bot</strong></summary>

1. Create a bot in the [Discord Developer Portal](https://discord.com/developers/applications).
2. Enable **Message Content Intent** and invite it with read, send,
   message-history, and **Manage Messages** permissions so `/clear` can remove
   user prompts.
3. Set **Messaging Platform** to **discord**.
4. Enter **Discord Bot Token**, **Allowed Discord Channels**, and an absolute **Allowed Directory**.
5. Apply the settings and restart the server if requested.

</details>

<details>
<summary><strong>Telegram bot</strong></summary>

1. Create a bot with [@BotFather](https://t.me/BotFather).
2. Get your numeric user ID from [@userinfobot](https://t.me/userinfobot).
   In groups, grant the bot permission to delete messages.
3. Set **Messaging Platform** to **telegram**.
4. Enter **Telegram Bot Token**, **Allowed Telegram User ID**, and an absolute **Allowed Directory**.
5. Apply the settings and restart the server if requested.

</details>

### Messaging commands

| Usage | Behavior |
| --- | --- |
| `/stats` | Show session state. |
| Standalone `/stop` | Cancel all work. |
| Reply with `/stop` | Cancel only the selected request while other queued requests continue. |
| Standalone `/clear` | Clear all FCC conversations and their messages in this chat. |
| Reply with `/clear` | Delete the selected message and the chain of replies to it. Keep other conversations. |

<details>
<summary><strong>Voice notes</strong></summary>

NVIDIA NIM transcription support is included in every installation. In **Admin UI → Messaging → Voice**, enable voice notes, select `nvidia_nim`, and choose a supported model. Configure your **NVIDIA NIM API key** on the Providers page.

For local Whisper on CPU or CUDA, stop FCC and re-run the installer (from
the clone, or replace `scripts/install.sh` with your downloaded
`fcc-install.sh`). Use the same agent you installed previously:

```bash
sh scripts/install.sh --agent codex --voice-local
```

For an NVIDIA GPU with CUDA 13.0:

```bash
sh scripts/install.sh --agent codex --voice-local --torch-backend cu130
```

Windows PowerShell:

Local Whisper on CPU or CUDA:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.ps1"))) -VoiceLocal
```

Local Whisper with CUDA 13.0:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install.ps1"))) -VoiceLocal -TorchBackend cu130
```

After installing local support, restart `fcc-server`. In **Admin UI → Messaging → Voice**, enable voice notes, select `cpu` or `cuda`, and choose the Whisper model. Local gated models need `HUGGINGFACE_API_KEY`.

</details>

## Manage Your Installation

Run `fcc-server --version` to check the installed version without starting FCC.

### Update

Stop all running FCC commands, then run:

```sh
fcc-update
```

If FCC is already up to date, the command stops without running the installer. Otherwise, it shows the installed and available versions before updating. If the version check fails, retry the command.

To reinstall FCC or change optional components while already up to date, run the [installer](#install) directly.

For local voice support, include `--voice-local` (macOS/Linux) or `-VoiceLocal` (Windows), plus your `--torch-backend` or `-TorchBackend` option if used.

If your installation does not have `fcc-update` yet, run the [installer](#install) once to add it.

### Muse Code on native Windows

To install or update only Muse Code:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/install-muse.ps1")))
```

To remove the Muse Code copy installed by FCC, keeping its data:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/uninstall-muse.ps1")))
```

Uninstalling FCC leaves Muse Code installed.

### Uninstall

Stop every running FCC command before uninstalling.

**Removes**

- Free Claude Code, including its desktop launcher and commands
- `~/.fcc/`

**Keeps**

- uv and Python
- Your coding agents and RTK

macOS/Linux (review the script before running; **this deletes** `~/.fcc/`):

```bash
curl -fL --progress-bar -o fcc-uninstall.sh "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/uninstall.sh"
```

If the download succeeded and you reviewed the file:

```bash
sh fcc-uninstall.sh
```

Windows PowerShell:

```powershell
& ([scriptblock]::Create((irm "https://raw.githubusercontent.com/Inkflow-Gab/claude-code-cli/main/scripts/uninstall.ps1")))
```

## Project Links

For a problem after installation, run the command below and paste its output into your bug report. It also copies the JSON to your clipboard when available.

```bash
fcc-doctor
```

- [Report bugs or request features](https://github.com/Inkflow-Gab/claude-code-cli/issues)
- [Contributing guide](CONTRIBUTING.md)

## Credits

This repository is a maintained copy of **Free Claude Code**, an independent
open-source project. All credit for the original project goes to its real owner
and repository:

- **Real owner:** [Alishahryar1](https://github.com/Alishahryar1)
- **Real repository:** [Alishahryar1/free-claude-code](https://github.com/Alishahryar1/free-claude-code)
- **Original installer:**

  ```bash
  curl -fsSL "https://raw.githubusercontent.com/Alishahryar1/free-claude-code/main/scripts/install.sh" | sh
  ```

This copy is published under the same `AGPL-3.0-only` license as the original.

## License

GNU Affero General Public License version 3 only (`AGPL-3.0-only`). See [LICENSE](LICENSE) for details.
