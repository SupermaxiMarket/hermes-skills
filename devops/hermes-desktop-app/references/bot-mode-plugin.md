# Bot Mode Plugin — Session Reference

Reference: hermes-desktop-app skill
Source: https://github.com/NousResearch/Hermes-Bot-Mode

## Plugin Structure

```
~/.hermes/desktop-plugins/hermes-bots/
└── plugin.js                # Main plugin file (Electron JS)
```

The plugin is a **desktop-only plugin** — it requires the Hermes Desktop Electron app, not the web dashboard.

## Bot Mode Architecture

- Each "bot" = an existing Hermes profile (`~/.hermes/profiles/<name>/`)
- Profiles already have: config, SOUL.md, memory, skills, credentials, chat history
- The plugin overlays a UI roster on top of profiles
- Creating/editing a bot uses `profiles.*` gateway RPCs
- Avatar generation uses `image.generate` RPC

## Key CLI Equivalent

Bot-to-bot messaging without the desktop app:

```bash
# Send message from one profile to another's inbox
hermes -p <from_profile> chat -c "Agent Inbox" -q "<message for <target_bot>>"
```

## Known Windows Installer Issue

The Hermes-Setup.exe installer on Windows can fail at the bootstrap stage with:

```
resolve install script failed: renaming ...\install-main.ps1.tmp → ...\install-main.ps1: Accès refusé.
```

This is caused by Windows Defender locking the downloaded `.ps1` file. Workarounds:
1. Pre-install ripgrep and ffmpeg via winget before running the installer
2. Add Windows Defender exclusion for `C:\Users\<user>\AppData\Local\hermes\`
3. Disable realtime monitoring temporarily
4. Or use the Linux/WSL desktop build instead (already pre-built)

## Per-Bot Model Pinning

Each bot in Bot Mode can use a different AI model. This is configured in the Advanced section when creating/editing a bot. This is the key differentiator from Grokbot — per-bot model choice.

## Per-Bot SOUL.md

Each bot has its own SOUL.md personality file (under its profile directory). This defines:
- How the bot talks
- What it cares about
- How it behaves
- The bot-to-bot messaging protocol (how to reply to other bots)

## Routines (Cron)

Routines are standard Hermes cron jobs namespaced `[bot:]`. They appear in both:
- The Bot Mode Routines pane
- `hermes cron list`

To create a routine for a bot:
```bash
hermes cron create "every day 9am" \
  --prompt "Summarize my inbox" \
  --profile <bot-profile>
```

## Notes from Beta

- Bot-to-bot delivery is per-invocation (receiving bot sees message on next run), no live interrupts yet
- Deleting a bot is CLI-only (no UI button to prevent accidental data loss)
- Plugin caches avatars/pets in plugin storage; the profile stays clean