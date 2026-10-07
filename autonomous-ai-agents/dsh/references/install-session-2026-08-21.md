# DSH Install — Session 2026-08-21

## Contexte

Installation de DeepSeek Harness (dsh) sur WSL (Ubuntu), exposé via cloudflared.

## Environnement

- Host: WSL2 (Windows Subsystem for Linux)
- Node.js: v22.22.2
- npm: 10.9.7
- DSH: v0.1.0-rc.7
- Cloudflared: /usr/local/bin/cloudflared

## Commandes exactes

```bash
# Install global
npm install -g @deepseek-ai/dsh
# Output: added 454 packages in 26s

# Verify
dsh --version
# 0.1.0-rc.7

# Launch web UI (background, no browser auto-open)
dsh web --no-open
# Binds to 127.0.0.1:3080

# Expose via cloudflared
cloudflared tunnel --url http://127.0.0.1:3080
# Output: https://restrict-dozen-trim-police.trycloudflare.com
```

## Processus en fond

| Process | PID | Commande |
|---------|-----|----------|
| dsh web | 5951 | `dsh web --no-open` (node process) |
| cloudflared | 5969 | `cloudflared tunnel --url http://127.0.0.1:3080` |

## URL

- Locale: http://127.0.0.1:3080
- Tunnel: https://restrict-dozen-trim-police.trycloudflare.com (éphemère)

## Notes

- npm a installé 454 packages, 66 avec funding notices, 1 deprecation warning (node-domexception).
- Aucune config supplémentaire nécessaire après `npm install -g`.
- La Web UI nécessite une clé API DeepSeek à configurer dans Settings → Models.
- Pas de fichier `.env` ou config locale créé par l'install — tout se fait via l'interface web.