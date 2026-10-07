# Free Backend Methods — Reference

Source: https://youtu.be/YuwGHABGmPw (Julian / AI Profit Warrior, mid-2026)

## The Four Methods

### Method 1: Local Model via Ollama
Cloud coding agent (Claude Code / Codex) tells a local Ollama model to do work.
- Install a local model via Ollama (e.g. LFM 2.5 2.6B)
- Tell the cloud agent: "Use [local model] as your engine for this task"
- Cloud model orchestrates via prompts
- Good for: private data, offline work, testing

### Method 2: Agent OS Orchestration
Claude Code / Codex controls the Agent OS (Hermes, etc.) directly.
- Agent OS runs in background with its own models
- Cloud coding agent delegates subtasks to Agent OS
- Cloud model remains the primary interface
- Good for: complex multi-step workflows, delegation

### Method 3: Multi-Model Harness (DSH)
DeepSeek Harness with dropdown model selector.
- Switch between local, free, and API models in one UI
- Fully open-source and customizable
- Access "creator mode" to add/remove providers
- Good for: power users who want full control

### Method 4: Free API Plug-In
Get a free API key (Token Harbor → DeepSeek V4.1 Flash) and plug it into Codex.
- Cloud model uses the free API as a subordinate worker
- No local GPU needed
- Token Harbor: DeepSeek V4.1 Flash free for ~2 weeks
- Good for: quick access to capable models without any setup

## Token Harbor Details
- Provider: Token Harbor (https://tokenharbor — verify URL)
- Model: DeepSeek V4.1 Flash
- Duration: ~2 weeks free (as of mid-2026)
- Integration: OpenAI-compatible API endpoint
- Use case: plug into Codex as a worker, not the primary agent