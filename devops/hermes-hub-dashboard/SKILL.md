---
name: hermes-hub-dashboard
description: "Use for web dashboard on port 8769: skill browse, search, install UI."
platforms: [linux]
---

# Hermes Hub Dashboard

Use when Pierre wants to manage skills visually, browse the Skills Hub, install from the web UI.

## Location

- Server: `/root/projets/hermes-hub/server.js`
- HTML dashboard: `/root/projets/hermes-hub/public/index.html`
- Port: **8769**

## Commands

```
# Start (with tunnel)
bash /root/projets/hermes-hub/hermes-hub.sh start

# Stop
bash /root/projets/hermes-hub/hermes-hub.sh stop

# Status
bash /root/projets/hermes-hub/hermes-hub.sh status
```

Bash aliases: `hub-start`, `hub-stop`, `hub-status`.

## Tunnel

Cloudflared tunnel auto-starts with `hub-start`. URL printed to status. Takes 3-5s to stabilize.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/skills` | GET | Installed skills (filesystem scan) |
| `/api/browse` | GET | Browse Skills Hub (page/size/source params) |
| `/api/search?q=` | GET | Search hub (--json output) |
| `/api/install` | POST | Install skill (body: {id}) |
| `/api/uninstall` | POST | Uninstall skill (body: {id}) |
| `/api/status` | GET | System status |

## Pitfalls

- `hermes skills list` has no `--json` — skills read from filesystem
- `hermes skills browse` has no `--json` — table output parsed server-side
- Only `hermes skills search` supports `--json`
- Kill stale node processes before start on port 8769
- An existing node `server/index.js` may occupy the port — kill it first