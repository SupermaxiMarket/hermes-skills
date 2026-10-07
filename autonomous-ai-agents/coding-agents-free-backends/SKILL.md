---
name: coding-agents-free-backends
description: "Run Claude Code with free Ollama or OpenRouter backends."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Free, Ollama, OpenRouter, Claude-Code, OpenCode]
    related_skills: [claude-code, opencode, codex]
---

# Coding Agents with Free Backends

How to run Claude Code, OpenCode, and similar coding agents without an Anthropic subscription, using free and open-source backends.

## Preferred Approaches (in order)

### 1. Ollama Native Integration (Zero-Config)

Since Ollama v0.14 (January 2026), Ollama exposes a native Anthropic Messages API. Launch any coding agent directly:

```
ollama launch claude --model <model>
ollama launch opencode --model <model>
ollama launch codex --model <model>
```

Ollama auto-sets `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`, and `ANTHROPIC_API_KEY`. No proxy, no manual config.

**Available integrations:** `claude`, `opencode`, `codex`, `hermes`, `chatgpt`, `cline`, `qwen`, `pi`, `kimi`, `copilot`, and more. Run `ollama launch --help` for the full list.

### 2. OpenRouter Free Models

When Ollama isn't viable (Cloud login broken, no GPU for local models), use OpenRouter's free models with OpenCode:

```
export OPENROUTER_API_KEY="<your-key>"
opencode --model openrouter/qwen/qwen3-30b-a3b:free
```

**Free models for coding (as of mid-2026):**

| Model | OpenRouter ID | Best For |
|-------|--------------|----------|
| Qwen 3 30B | `qwen/qwen3-30b-a3b:free` | Strong code gen |
| Gemma 3 27B | `google/gemma-3-27b-it:free` | All-round coding |
| DeepSeek Chat | `deepseek/deepseek-chat:free` | Complex reasoning |
| Llama 3.3 70B | `meta-llama/llama-3.3-70b-instruct:free` | Large context |
| Mistral 7B | `mistralai/mistral-7b-instruct:free` | Fast, lightweight |

### 3. Ollama Local Models

No login needed, fully offline:

```
ollama pull qwen3:32b
ollama launch claude --model qwen3:32b
```

Recommended local models: `qwen3:32b` (code-optimized), `codellama:13b` (smaller), `deepseek-coder-v2` (strong reasoning).

### 4. Ollama Cloud Models (⚠️ PAYWALLED as of Aug 2026)

Hosted on Z.ai servers, no GPU needed, but since ~August 2026 they **require a paid Ollama plan**. Verified 2026-08-12: `glm-5.2:cloud` and `deepseek-v4-flash:0731-cloud` both fail with `403 Forbidden: this model requires a subscription, upgrade for access: https://ollama.com/upgrade` — via CLI, via `ollama launch claude --model ...`, and via the local OpenAI-compatible API (`localhost:11434/api/chat`). `ollama login` no longer unlocks them.

Free alternatives when cloud models are blocked:
- **Local models** (no login, offline): `ollama pull qwen3:8b` then `ollama launch claude --model qwen3:8b`
- **OpenRouter free models**: `opencode --model openrouter/nvidia/nemotron-3-ultra-550b-a55b:free` (Nemotron 550B) or `.../deepseek/deepseek-chat:free`
- Note: `ollama pull` of a large local model (4-30GB) can take 10+ min and timeout in sandboxed environments — start with 8B-class models.

## Pitfalls

### Claude Code v2.x Auth Gate
Claude Code v2.1+ shows an OAuth login screen on first launch and **blocks even with `ANTHROPIC_API_KEY` set to a dummy value**. Environment variables alone cannot bypass this. Solutions:
- Use `ollama launch claude` (handles auth automatically)
- Use OpenCode (no Anthropic auth check)
- If you have a real Anthropic account, use `claude auth login` once

### Ollama Login on WSL
`ollama login` opens a browser link for authentication. On WSL, the browser opens on Windows but the callback to the WSL Ollama process often **hangs indefinitely** on "Waiting for sign in to complete...". Workarounds:
1. Use local models (no login needed)
2. Use OpenRouter free models
3. Run Ollama natively on Windows, connect from WSL via `OLLAMA_API_BASE=http://172.31.64.1:11434`
4. Run `ollama login` from a native Linux terminal/VM

### Large Model Pulls on Slow Connections
Models 20GB+ (32B params and above) can take 10+ minutes to pull and may timeout in sandboxed environments. Start with smaller models (7B-13B) or use cloud/API backends for immediate results.

### Proxy Is Obsolete for Ollama
The `claude-code-ollama-proxy` (LiteLLM-based, port 8082) was the pre-v0.14 workaround. Since Ollama's native Anthropic API, proxies are **unnecessary for Ollama backends**. They remain useful for non-Ollama backends (NVIDIA NIM, custom endpoints).

### 5. Free API Providers (Token Harbor pattern)

Some services offer temporary free API access to high-end models. The pattern: get a free API key, plug it into your coding agent, and let the cloud model orchestrate it.

**Token Harbor** (mentioned by Julian / AI Profit Warrior, mid-2026):
- DeepSeek V4.1 Flash — free for ~2 weeks
- Plug directly into Codex/Claude Code via OpenAI-compatible endpoint
- The cloud model orchestrates the free API as a subordinate worker
- Pattern: `cloud model controls free API → delegates heavy work`

**When to use this:**
- You need a capable model (DeepSeek V4.1 Flash) without paying
- You want to keep your primary agent (Claude Code/Codex) as the orchestrator
- The free API serves as a worker, not the main agent

**Limitations:** Temporary (2-week window), rate-limited, provider can shut off anytime.

---

## The Four Methods (from the video)

The video (youtu.be/YuwGHABGmPw) presents four approaches to combine coding agents with free/local models:

1. **Local model via Ollama** — Coding agent delegates work to a locally-installed model (e.g. LFM 2.5 2.6B). Cloud model orchestrates local model via prompt commands.
2. **Agent OS orchestration** — Claude Code / Codex controls the Agent OS (Hermes, etc.) directly. Cloud model remains the interface, Agent OS executes subtasks.
3. **Multi-model harness (DSH)** — DeepSeek Harness with dropdown selectors: switch between local, free, and API models in one UI. Most customizable but most complex.
4. **Free API plug-in** — Token Harbor, etc. Free API key plugged into Codex/Claude Code. Cloud model delegates to the free API as a worker.

## Verification

Smoke test with Ollama:
```
ollama launch claude --model <model> -y
# Should launch Claude Code TUI directly, no auth prompt
```

Smoke test with OpenRouter:
```
opencode run 'Reply exactly: BACKEND_OK' --model openrouter/google/gemma-3-27b-it:free
# Should output BACKEND_OK
```

## Related

- `claude-code` skill — full Claude Code CLI reference (bundled)
- `opencode` skill — OpenCode CLI reference (bundled)
- NVIDIA NIM: build.nvidia.com — GLM 5.2 available with free API key (40 req/min)
- Z.ai Coding Plan: z.ai — direct GLM 5.2 access via OpenAI-compatible API