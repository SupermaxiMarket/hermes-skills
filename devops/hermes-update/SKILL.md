---
name: hermes-update
description: "Keep Hermes Agent up to date proactively."
version: 1.0.0
author: Pierre Andre Erard
license: MIT
metadata:
  hermes:
    tags: [hermes, update, maintenance]
---

# Hermes Update Maintenance Skill

This skill captures the practice of proactively checking for and applying Hermes Agent updates to ensure you have the latest features, performance improvements, and security fixes.

## Why Proactive Updates?

- Major releases (v0.19 "Quick Silver", v0.20 "Herald", etc.) ship game-changing features like voice, wake word, A2A, artifacts, smart approvals, and massive speed gains.
- Staying current reduces compatibility issues and unlocks the latest toolsets.
- Regular updates are part of a professional workflow; waiting for a user prompt can delay benefits.

## Recommended Workflow

1. **Back up your profiles first**:
   ```bash
   cp -r ~/.hermes/profiles ~/.hermes/profiles.backup
   ```
2. **Check for updates** (run at the start of a session or daily):
   ```bash
   hermes update --check
   ```
3. **If updates are available**, apply:
   ```bash
   hermes update --yes   # auto‑accept prompts
   ```
4. **Verify**:
   ```bash
   hermes --version
   hermes profile list
   hermes profile info <your-profile>
   ```
5. **Sync features** across profiles (see post-update section below).

## Post-update: Activate new features

After every update, check and enable newly available capabilities. These are the features that typically ship inactive by default:

```bash
# 1. Max reasoning (for deep work profiles)
hermes config set agent.reasoning_effort max

# 2. Live reasoning display (transparency — useful across all profiles)
hermes config set display.show_reasoning true

# 3. Smart approvals (AI judges when to interrupt, fewer prompts)
hermes config set approvals.mode smart

# 4. Enable voice/TTS (v0.20+)
hermes config set voice.enabled true
hermes config set voice.auto_tts true           # auto text-to-speech replies
hermes config set voice.barge_in true           # mid-turn interruption by voice

# 5. Wake word (v0.20+)
hermes config set wake_word.enabled true
```

Propagate to custom profiles:
```bash
hermes config set agent.reasoning_effort max --profile agent-os
hermes config set display.show_reasoning true --profile agent-os
hermes config set approvals.mode smart       --profile agent-os
# Repeat for agent-os-fast, agent-os-nemotron, romancier, etc.
```

### Feature checklist (v0.20 "Herald")

| Feature | Config / command | Recommended | Notes |
|---------|-----------------|-------------|-------|
| Ultra-fast first token | Built-in | Automatic | ~0.9s vs 4.3s (v0.19) |
| Max reasoning | `agent.reasoning_effort: max` | Deep work | Deeper analysis |
| Live reasoning | `display.show_reasoning: true` | All profiles | See model think |
| Smart approvals | `approvals.mode: smart` | Always | Fewer interruptions |
| Talk to Hermes (voice) | `voice.enabled: true` + `auto_tts: true` | Interactive | Real-time speech |
| Wake word | `wake_word.enabled: true` | Hands-free | Say "Hey Hermes" |
| Barge-in (interrupt) | `voice.barge_in: true` | Natural flow | Cut off mid-response |
| Grounded citations | `grounded-citations` skill (builtin) | Research | Source-backed answers |
| A2A (Agent-to-Agent) | `hermes acp` + `hermes plugins install agent-to-agent` | Multi-agent | Discover & collaborate |
| Desktop Artifacts | `hermes desktop` | Heavy users | Sandboxed live previews |
| Mid-turn correction | Built-in | All | Redirect without /stop |
| Smarter compression | Built-in | Automatic | Recent conv always survives |
| Outbound webhooks | `hermes webhook` | Automation | Notify external systems |
| Session export | `hermes sessions export` | On demand | Portability |
| Secrets manager | `hermes secrets` | If using Bitwarden | Secure API keys |
| Bundled skills | Auto-synced | Automatic | Check `hermes skills list` |

### New bundled skills in v0.20

Check with `hermes skills list --all` — includes grounded-citations, research-paper-writing, plus creative skills (excalidraw, pixel-art, sketch, baoyu-comic, baoyu-infographic, pretext, claude-design, manim-video, etc.), productivity (kanban-manager, nano-pdf, ocr-and-documents, mission-control-dashboard, etc.), data science (jupyter-live-kernel), and more.

## Notes

- The update process only modifies the Hermes Agent core, bundled skills, and default configuration. Your personal files under `~/.hermes/profiles/<name>/` (sessions, memories, custom skills, etc.) are never touched.
- After a major version bump, run `hermes config migrate` if needed to bring `config.yaml` up to date.
- If you encounter git stash conflicts in non‑essential files, use `git stash apply` to restore them.
- **WSL note**: the git-based update fetches from origin and rebuilds via uv; it takes ~1-2 minutes for minor, ~3-5 minutes for major.

## Reference

- Official docs: https://hermes-agent.nousresearch.com/docs/user-guide/profiles/#profile-builder-updating-hermes-agent
- v0.20 "Herald" release: https://youtu.be/AdGgO8zuaYM