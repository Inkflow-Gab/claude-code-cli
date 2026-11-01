# Coding agents and launchers

Install FCC and configure a provider using the [quick start](../README.md#quick-start) first.
These commands run on the machine hosting FCC.


Claude Code:

```bash
fcc-claude
```

Codex:

```bash
fcc-codex
```

Pi:

```bash
fcc-pi
```

OpenCode 2:

```bash
fcc-opencode
```

To upgrade from OpenCode 1, close OpenCode and rerun the FCC installer with
OpenCode selected. For npm or other package-manager installations, follow
[OpenCode's migration instructions](https://opencode.ai/v2/docs/migrate-v1/)
first. For npm v1, run `npm uninstall -g opencode-ai`, then rerun the FCC installer.

RTK integration is temporarily unavailable for OpenCode 2. RTK continues to work
with the other supported agents.

Use `fcc-opencode` for coding and sessions. Use plain `opencode` for commands
such as upgrades, service management, ACP, and MCP setup.

Cline:

```bash
fcc-cline
```

Hermes:

```bash
fcc-hermes
```

DeepSeek Harness Web:

```bash
fcc-dsh
```

For DeepSeek Harness Desktop, install and open the app once, then select **Connect** under **Integrations → DeepSeek Harness Desktop** in FCC. Keep FCC running while using its models. FCC becomes the default for new sessions. Select **Disconnect** to remove the connection. Native DeepSeek account features still need a DeepSeek login.

Use DeepSeek Harness 0.2.0-rc.2 or newer. Update the CLI with:

```bash
npm install -g @deepseek-ai/dsh@latest
```

For headless tasks, run `fcc-dsh headless "your task"`. Extra `--patch` files apply after FCC's settings. After disconnecting Desktop, select another model to continue an existing FCC session. If another DSH setting uses FCC's Desktop credential, Disconnect keeps that credential and reports why.

Grok Build:

```bash
fcc-grok
```

Muse Code:

```bash
fcc-muse
```

Aider:

```bash
fcc-aider
```

<a id="model-picker"></a>

<div align="center">
  <img src="../assets/cc-model-picker.png" alt="Claude Code model picker showing FCC models" width="700">
  <p><em>Select an FCC model from Claude Code's native <code>/model</code> picker.</em></p>
</div>
