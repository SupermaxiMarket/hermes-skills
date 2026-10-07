# Cloudflared tunnel from WSL — Session 2026-08-08

## Contexte

Déploiement de Vigilance Commerce (Next.js 16.3 + Prisma 7) sur
`https://practices-cube-microwave-programmers.trycloudflare.com`

## Commandes exactes

```bash
# Kill old tunnels
pkill -f cloudflared

# Start tunnel (daemonized from Python: preexec_fn=os.setsid)
cloudflared tunnel --url http://localhost:3000
```

Le log produit une ligne : `Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):`
suivie de `https://<random>.trycloudflare.com`

## Serveurs en fond (à vérifier avec `ps aux | grep`)

| Process | PID (session) | Commande |
|---------|---------------|----------|
| next dev | 2005/2017/2018/2030 | npx next dev --port 3000 |
| cloudflared | 2175 | cloudflared tunnel --url http://localhost:3000 |

## Logs

- Next.js: `/tmp/vigilance-next.log`
- Cloudflared: `/tmp/cloudflared-vigilance.log`
- URL sauvegardée: `/tmp/vigilance-current-url.txt`

## Test de vérification

```bash
# Pages publiques
curl -s -o /dev/null -w "%{http_code}" https://<url>/login   # 200
curl -s -o /dev/null -w "%{http_code}" https://<url>/register # 200

# Pages protégées (redirect vers login sans session)
curl -s -o /dev/null -w "%{http_code}" https://<url>/dashboard  # 307
curl -s -o /dev/null -w "%{http_code}" https://<url>/stores     # 307
curl -s -o /dev/null -w "%{http_code}" https://<url>/alerts     # 307
curl -s -o /dev/null -w "%{http_code}" https://<url>/map        # 307
```

## Erreurs évitées

- serveo.net: `ssh: connect to host serveo.net port 22: Connection timed out` — ne pas insister
- localhost.run: hang indéfini