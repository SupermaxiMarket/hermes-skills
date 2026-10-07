---
name: omniroute-management
description: Manage OmniRoute AI gateway — install, providers, routing.
version: 1.0.0
author: Pierre Erard / Hermes
platforms: [linux, macos]
---

# OmniRoute Management

## Installation
`npm install -g omniroute` — binary at `/root/.hermes/node/bin/omniroute`.

## Startup (localhost-only)
```bash
OMNIROUTE_SERVER_HOST=127.0.0.1 omniroute serve --daemon
```

Script: `/root/projets/agent-os/omniroute.sh start|stop|status|dash`
Aliases in ~/.bashrc: `omniroute-start/stop/status/dash`.

## Dashboard
http://localhost:20128 — password: `omniroute2026`
Providers: http://localhost:20128/dashboard/providers

## Providers

### No-auth (no key): opencode, aihorde
- opencode: only from OpenCode CLI (403 outside it)
- aihorde: free but models change often — `omniroute radar sync`

### Free API-key (get key at provider website, add via dashboard or CLI):
```bash
omniroute setup --add-provider --provider <id> --api-key <key>
```
Best bets: **gemini**, **cloudflare-ai**, **groq**, **mistral**, **cohere**

### Web-cookie: need browser cookie capture via dashboard.

## Combos (routing)
```bash
omniroute combo create <name> --models "provider/model1,provider/model2"
omniroute combo switch <name>
```

## Hermes integration (fallback)
```yaml
fallback_providers:
  - provider: openrouter
    base_url: http://localhost:20128/v1
    api_key: <omniroute-api-key>
    model: auto
```

## Troubleshooting
- 0 models: connect a provider first
- opencode 403: normal — not usable as generic API
- aihorde model fails: `omniroute radar sync` to refresh catalog