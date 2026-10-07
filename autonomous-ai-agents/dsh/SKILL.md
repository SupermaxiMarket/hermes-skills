---
name: dsh
description: "Use DeepSeek Harness (dsh), an open-source agent runtime."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, DSH, DeepSeek-Harness, Autonomous, Web-UI]
    related_skills: [claude-code, codex, opencode, hermes-agent]
---

# DeepSeek Harness (dsh)

[DeepSeek Harness](https://github.com/deepseek-ai/dsh) (dsh) is a free (MIT), TypeScript-based agent runtime that turns any DeepSeek model into an autonomous coding/automation worker. Launched mid-August 2026, it reached 95K GitHub stars in 48h. Still in developer preview (v0.1.x) — breaking changes possible.

## When to Use

- User mentions "DeepSeek Harness", "DSH", or asks to install/run it
- You need an alternative coding agent alongside Claude Code / Codex / OpenCode
- User wants to run DeepSeek models as an autonomous agent with file, shell, and web access
- You need a web UI for agent interaction (DSH runs a browser interface)

## Architecture

DSH uses a **profile system** — each profile is a plugin-bundle stack:

| Profile | Mode | Use Case |
|---------|------|----------|
| `web` | Web UI (default port 3080) | Interactive browser-based agent sessions |
| `tui` | Terminal / headless | One-shot tasks, automation, background jobs |
| custom | Via `--profile <name>` | User-defined plugin stacks |

DSH is NOT an agent framework you import — it's a bootable runtime you launch per-project.

## Prerequisites

- **Node.js ≥ 22.19** (24+ recommended). Check: `node --version`
- **npm** (ships with Node)
- **DeepSeek API key** from https://platform.deepseek.com (billing: very cheap, free tier available)
- **Cloudflared** (optional, for public tunnel): `which cloudflared`

## Installation

### Global install (recommended for CLI access)

```bash
npm install -g @deepseek-ai/dsh
```

Single-command alternative (auto-downloads & runs, no global install):

```bash
npx @deepseek-ai/dsh web
```

Verify:

```bash
dsh --version     # e.g. 0.1.0-rc.7
dsh --help        # shows available profiles and commands
```

### Upgrade

```bash
npm update -g @deepseek-ai/dsh
```

Since this is v0.1.x dev preview, check for updates before each use.

## Usage

### Web UI (interactive, browser-based)

```bash
# Default: port 3080, auto-opens browser
dsh web

# Custom port, no auto-open
dsh web --port 3080 --no-open

# Custom host binding
dsh web --host 0.0.0.0 --port 3080
```

**First-time setup in the UI:**
1. Open http://127.0.0.1:3080
2. Go to Settings → Models
3. Paste your DeepSeek API key
4. Select model (e.g. `deepseek-v4-flash` for speed, `deepseek-v4-pro` for complex tasks)
5. Select a workspace directory (the project folder DSH will operate on)
6. Start giving orders

### Headless / One-Shot Tasks (TUI profile)

```bash
# Execute a task and exit (prints result to stdout)
dsh --profile tui "Read all files in this directory and write a README.md"
```

Best for: automation scripts, CI/CD integration, batch processing.

### Public Tunnel (cloudflared)

Expose the Web UI externally:

```bash
cloudflared tunnel --url http://127.0.0.1:3080
```

Outputs: `https://<random>.trycloudflare.com`

### Plugin Management

```bash
# Add a plugin to the web profile
dsh plugin --profile web add <package-name>

# List plugins
dsh plugin --profile web list
```

### Config & Profiles

DSH stores profiles under `$DSH_HOME/profiles/`.

Dump the effective config:

```bash
dsh --dump-config              # with user overrides
dsh --dump-default-config      # base profile only
```

Custom profiles can be created with override patches (YAML):

```bash
dsh --profile tui --patch ./my-overrides.yml "Run the data pipeline"
```

## Session Management

DSH web sessions persist in the browser (localStorage/sessionStorage). Headless (`tui`) sessions are ephemeral — output is printed to stdout on completion.

To resume a headless session:

```bash
dsh --profile tui --resume <session-id>
```

## Model Configuration

Configured via Web UI (Settings → Models) or potentially via config YAML in the profile.

DSH supports **multi-model dropdowns** in the web UI — you can add local, free, and API models side-by-side and switch mid-session. This is done via "creator mode" or profile patching.

Recommended model choices:

| Task Type | Model | Why |
|-----------|-------|-----|
| Quick tasks, code review | `deepseek-v4-flash` | Fast, cheap |
| Complex reasoning, refactors | `deepseek-v4-pro` | More capable |

**Multi-model setup** (from Julian / AI Profit Warrior):
1. Go to Settings → Models in the web UI
2. Add multiple providers (DeepSeek API + local Ollama + free API endpoints)
3. Use the dropdown to switch between them during a session
4. For more customization, use `--profile custom` with YAML override patches

## Procedure

1. **Check prerequisites**: `node --version`, verify npm works, confirm DeepSeek API key exists
2. **Install** if missing: `npm install -g @deepseek-ai/dsh`
3. **Verify install**: `dsh --version` (expect ≥ 0.1.x)
4. **Choose mode**:
   - **Web UI** for interactive work: `dsh web` → configure API key in Settings
   - **Headless** for automation: `dsh --profile tui "task description"`
5. **Optionally expose** with `cloudflared tunnel --url http://127.0.0.1:3080`
6. **Report back**: URL and mode used

## Integration with Hermes Agent

DSH can be orchestrated from Hermes as a subordinate agent:

```bash
# Launch DSH web in background
nohup dsh web --no-open &>/tmp/dsh.log &
echo $! > /tmp/dsh.pid

# Or run a headless task from Hermes
result=$(dsh --profile tui "Analyze ./src/ for security issues" 2>&1)
```

### Live Processes Management

```bash
# List running DSH processes
ps aux | grep dsh

# Kill DSH web
kill $(cat /tmp/dsh.pid)

# Kill all DSH processes
pkill -f "dsh.*web"
pkill -f "node.*dsh"
```

## Smoke Test

```bash
# Quick smoke test (headless)
dsh --profile tui "Output exactly: DSH_SMOKE_OK" 2>&1 | grep -q DSH_SMOKE_OK && echo "DSH OK" || echo "DSH FAIL"

# Web UI port check
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3080  # Expect 200 if running
```

## Pitfalls

- **v0.1.x dev preview**: APIs, config formats, and plugin interfaces may break between releases.
- **Node version**: Must be ≥ 22.19. Older LTS versions silently fail.
- **API key required**: DSH won't operate without a configured DeepSeek API key. Configure in Web UI Settings → Models.
- **First launch slow**: `npx @deepseek-ai/dsh web` downloads the full package on first run (20-30s).
- **Cloudflared tunnels are ephemeral**: URL changes on every restart. No persistence guarantee.
- **WSL networking**: DSH binds `127.0.0.1:3080` by default. For external access, use cloudflared or bind `--host 0.0.0.0`.
- **Parallel instances**: Running multiple DSH web instances on the same port fails. Use `--port 0` to let the OS assign a free port.

## Comparison: DSH vs Other Coding Agents

| Tool | Runtime | Interface | License | Model |
|------|---------|-----------|---------|-------|
| **DSH** | Node.js | Web UI + headless | MIT (free) | DeepSeek only (API) |
| Claude Code | Node.js | CLI/TUI | Proprietary | Claude only |
| Codex | Python | CLI/TUI | MIT | OpenAI/any |
| OpenCode | Node.js | CLI/TUI | MIT | Provider-agnostic |

## Verification Checklist

- [ ] `node --version` ≥ 22.19
- [ ] `dsh --version` returns a version
- [ ] Web UI: `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3080` = 200
- [ ] API key configured in Settings → Models
- [ ] Workspace directory selected
- [ ] Headless mode works: `dsh --profile tui "echo test"`
- [ ] (Optional) Tunnel accessible from public URL