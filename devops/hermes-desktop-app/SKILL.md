---
name: hermes-desktop-app
description: "Launch Hermes Desktop on WSL and manage desktop plugins."
version: 1.0.0
author: Hermes Agent
platforms: [linux, wsl]
metadata:
  hermes:
    tags: [hermes, desktop, electron, wsl, plugins, bot-mode]
    related_skills: [hermes-agent, hermes-update, hermes-dashboard]
---

# Hermes Desktop App (Electron)

The Hermes Desktop is an Electron-based GUI application that wraps the Hermes Agent. It provides a roster UI (Sessions + Bots tabs), desktop plugins, and integrates with WSLg for display on Windows via WSL.

**This is distinct from the web dashboard** (`hermes dashboard` at port 9119). The desktop app loads plugins from the filesystem and has its own plugin SDK.

## Locating the Desktop App

The desktop app is built during `hermes update` and lives inside the Hermes install directory:

```bash
# Linux/WSL path
/usr/local/lib/hermes-agent/apps/desktop/release/linux-unpacked/Hermes

# Check if it exists
ls -la /usr/local/lib/hermes-agent/apps/desktop/release/linux-unpacked/Hermes

# Check build stamp
cat ~/.hermes/desktop-build-stamp.json
# → "sourceMode": false means built, "sourceMode": true means needs build
```

## Launching on WSL with WSLg

WSLg (Windows Subsystem for Linux GUI) provides X11/Wayland compositing, so the Electron app renders directly on the Windows desktop.

```bash
# Required environment variables
DISPLAY=:0
XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
WAYLAND_DISPLAY=wayland-0
PULSE_SERVER=/mnt/wslg/PulseServer

# Launch command
XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir \
DISPLAY=:0 \
WAYLAND_DISPLAY=wayland-0 \
PULSE_SERVER=/mnt/wslg/PulseServer \
/usr/local/lib/hermes-agent/apps/desktop/release/linux-unpacked/Hermes \
  --no-sandbox
```

The `--no-sandbox` flag is required when running as root (WSL default).

## Desktop Plugins

Desktop plugins are JS files loaded by the Electron app from `~/.hermes/desktop-plugins/<plugin-name>/plugin.js`.

### Installing a plugin

```bash
mkdir -p ~/.hermes/desktop-plugins/<plugin-name>
curl -L -o ~/.hermes/desktop-plugins/<plugin-name>/plugin.js <url>
```

### Reloading plugins

After adding or updating a plugin, reload in the running desktop app:

- **Keyboard**: Ctrl+K (or Cmd+K on Mac) → type "Reload desktop plugins" → Enter
- **Restart**: kill the Hermes process and relaunch

### Bot Mode Plugin

The Bot Mode plugin turns agent profiles into a roster of named bots with avatars, routines, and bot-to-bot messaging.

- **Repo**: https://github.com/NousResearch/Hermes-Bot-Mode
- **Plugin URL**: https://raw.githubusercontent.com/NousResearch/Hermes-Bot-Mode/main/plugin.js

```bash
mkdir -p ~/.hermes/desktop-plugins/hermes-bots
curl -L -o ~/.hermes/desktop-plugins/hermes-bots/plugin.js \
  https://raw.githubusercontent.com/NousResearch/Hermes-Bot-Mode/main/plugin.js
```

After reloading plugins, a **Bots** tab appears next to Sessions in the desktop app.

### How Bot Mode works

A bot is a Hermes profile — each has its own config, memory, skills, and chat history. The plugin provides a UI over this primitive:

- **Bots pane** — left-side roster with avatars, message previews
- **Routines** — recurring tasks per bot, backed by Hermes cron
- **Bot-to-bot** — agents message each other via `hermes -p <profile> chat -c "Agent Inbox"`
- **@mentions** — `@researcher` in any chat hands off to that bot

## Troubleshooting

### "Missing X server or $DISPLAY"

The DISPLAY environment variable is not set or the X server is inaccessible.

**On WSL with WSLg**:
- WSLg should auto-start. Check that `/tmp/.X11-unix/X0` exists (world-writable socket).
- Set `DISPLAY=:0`, `XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir`, `WAYLAND_DISPLAY=wayland-0`

**On Linux without WSLg**:
- Ensure an X server is running (Xorg, Xvfb, or a desktop environment)
- Set `DISPLAY=:0` (or the correct display number)

### WSL GPU passthrough

The app detects `/dev/dxg` and enables GPU acceleration automatically. If you see GPU-related crashes, add `--disable-gpu-sandbox`.

### Desktop app starts then immediately exits

Common causes:
- Missing DISPLAY environment variable
- Running as root without `--no-sandbox`
- Missing X11 libraries: `apt-get install libx11-xcb1 libxcomposite1 libxdamage1 libxfixes3 libxrandr2`

### Plugin not showing

- Verify the plugin path: `~/.hermes/desktop-plugins/<name>/plugin.js` (the directory name matters)
- Reload plugins: Ctrl+K → "Reload desktop plugins"
- Check the plugin file is valid JS (not truncated download)
- Restart the app entirely

### Electron window not appearing on Windows (WSLg)

The app process is running but the window doesn't render on the Windows desktop. Check:
```bash
grep Hermes /mnt/wslg/weston.log         # Window registered?
cat ~/.config/Hermes/window-state.json     # Position/size off-screen?
```
If the app registered with Weston but no window appears, the WSLg→RDP bridge isn't forwarding it. This can happen when running as root in WSL (Wayland socket owned by UID 1000, process runs as root). **No reliable fix from headless WSL** — the web dashboard or a custom web UI are the fallback.

### Windows installer fails with "Accès refusé (os error 5)"

The Hermes Desktop installer (`Hermes-Setup.exe`) downloads `install.ps1` into `bootstrap-cache/install-main.ps1.tmp` and renames it. **Windows Defender locks the `.tmp` file.**

Workarounds (in order):
```powershell
# 1. Add exclusion + disable real-time monitoring
Add-MpPreference -ExclusionPath "C:\Users\<user>\AppData\Local\hermes"
Set-MpPreference -DisableRealtimeMonitoring $true

# 2. Clean slate + retry
Stop-Process -Name "Hermes-Setup" -Force
Remove-Item "C:\Users\<user>\AppData\Local\hermes" -Recurse -Force

# 3. Pre-install ripgrep + ffmpeg (first-failing stage)
winget install -e --id BurntSushi.ripgrep.MSVC
winget install -e --id Gyan.FFmpeg

# 4. Run installer again
Start-Process "C:\Users\<user>\AppData\Local\Temp\Hermes-Setup.exe"
```

If none work, the Linux desktop build is already present after `hermes update` — skip the Windows installer.

## Web-based Bot Mode fallback

If the Electron desktop app window doesn't render (WSLg) or the Windows installer fails, build a lightweight web-based Bot Mode UI instead. The pattern:

1. **Start a local HTTP server** (Python http.server, FastAPI, etc.)
2. **Proxy the Hermes REST API** at `localhost:9119` — keep the `/api/` prefix intact (critical: forwarding `/profiles` returns HTML, not JSON)
3. **Chat via CLI subprocess**: `hermes -p <profile> chat -q "<message>"` captures stdout as the bot reply
4. **Serve an HTML roster** listing profiles from `GET /api/profiles`, each clickable to open a per-bot chat view
5. **Show routines** via `GET /api/cron/jobs`

This gives the bot-roster + per-bot-chat experience without the Electron app. The example at `/root/projets/bot-mode-web/server.py` demonstrates the full pattern (API proxy + CLI subprocess chat + HTML roster).

## Related

- `hermes dashboard` — web-based UI (port 9119), different from the Electron desktop app
- `hermes update` — rebuilds the desktop app when Hermes is updated
- `hermes profile list` — profiles that appear as bots in Bot Mode