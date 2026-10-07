---
name: session-context-restoration
description: >-
  Recover session context fast (<60s). Use when resuming work.
---

# Session Context Restoration

Reprendre le travail d'une session précédente sans perdre 10 minutes à tout redécouvrir.

## Déclencheur

Utiliser CE SKILL quand l'utilisateur dit « reprends », « on continue », « retrouve la session », ou cite un projet existant. Ne pas commencer par fouiller les fichiers — passer par le store de sessions.

## Workflow (30-60 secondes max)

### 1. Lister les sessions récentes
```bash
hermes sessions list
```
Identifier la bonne session par :
- **Titre** (colonne `Title` — correspond souvent au sujet)
- **Horodatage** (`Last Active` — la plus récente = candidate)
- **ID** gardé pour l'export

⚠️ L'utilisateur s'énerve si ça prend plus de 60 secondes. **Pas de fluff.**

### 2. Exporter la session
```bash
hermes sessions export --session-id <ID> --format md /tmp/ctx
```
Format `md` = un fichier markdown lisible avec tous les messages.

### 3. Lire l'export
```bash
# Lire l'en-tête (métadonnées: modèles, stats)
head -30 /tmp/ctx/<fichier>.md

# Lire la fin (dernier état, ce qui a été fait, URLs)
tail -60 /tmp/ctx/<fichier>.md
```

### 4. Extraire l'état critique
À partir de l'export, relever :
- **Ports** et URLs (serveurs, tunnels)
- **Fichiers modifiés**
- **Décisions prises** (ce qui est fait, ce qui reste)
- **Blocages** (raison pour laquelle la session s'est arrêtée)

### 5. Vérifier le runtime
```bash
# Ports ouverts
ss -tlnp | grep -E '8760|3000|8765|8768|8899|51763'

# Processus (serveurs, tunnels)
ps aux | grep -E 'cloudflared|node.*vaulty|node.*hermes|node.*3000|python3.*http'
```

### 6. Présenter le résumé
Format attendu par l'utilisateur :
- ✅ Ce qui est opérationnel (port, URL, statut HTTP)
- ❌ Ce qui est cassé ou bloqué
- ⚡ Prochaine action (une seule, pas un plan)

## Pièges

- **Ne pas refaire ce qui est déjà fait** — toujours partir de l'état de la session
- **Tunnels cloudflared** : après reboot → nouvelle URL random. Le DNS custom (budgetfamilial.men) ne marche pas sans auth Cloudflare (lien à cliquer)
- **Ne pas présenter des projets non liés** — juste ce qui est demandé
- **Ne pas demander de confirmation pour chaque étape** — exécuter directement
- **Si l'export échoue** → `hermes sessions list | grep <project>` → `hermes sessions export --session-id` avec le préfixe d'ID
- **`hermes sessions export` peut crasher si pas d'argument output** — toujours fournir un chemin absolu

## Reboot recovery

Quand l'utilisateur signale un reboot / PC rallumé / « le PC a planté » :

### Vérifier les services critiques

Après un reboot WSL, TOUT est mort. Ne pas fouiller les sessions — vérifier le runtime d'abord :

```bash
ss -tlnp | grep -E '3000|9120|18789|8760|8765'
```

Anticiper les ports qui peuvent être absents (service non lancé) et ne pas paniquer — le recovery qui suit liste l'ordre de relance.

**Stack Hermes3D** (3 processus indépendants) :
1. **`hermes serve`** (port 9120) — backend JSON-RPC. Relancer avec `HERMES_DASHBOARD_SESSION_TOKEN=<token> hermes serve --host 127.0.0.1 --port 9120 --skip-build`
2. **Node Studio** (port 3000) — `node server/index.js` dans `/root/projets/hermes-3d/` avec `UPSTREAM_ALLOWLIST=localhost,127.0.0.1`
3. **Gateway Adapter** (port 18789) — `node server/hermes-gateway-adapter.js` dans `/root/projets/hermes-3d/` avec `HERMES_API_URL` + `HERMES_API_KEY`

**Stack Budget** :
1. **HTTP server** (port 8760) — `python3 -m http.server 8760` dans `/root/projets/budget-suisse/`

**Stack Vaulty** :
1. **Node server** (port 8765) — `node server/server.js` dans `/root/projets/vaulty/`
2. **Tunnel** (cloudflared) — `bash /root/projets/vaulty/tunnel.sh`

### Tunnels changent à chaque reboot

Les URLs cloudflared sont éphémères et changent à chaque restart. Lire les nouvelles URLs :
```bash
cat /tmp/hermes3d-url.txt 2>/dev/null
cat /tmp/budget-url.txt 2>/dev/null
cat /tmp/vaulty-url.txt 2>/dev/null
```
Ou extraire des logs : `grep -oE 'https://[a-z0-9-]+\\.trycloudflare\\.com' /tmp/hermes3d-tunnel.log /tmp/vaulty-tunnel.log`

### Ordre de recovery

1. `hermes serve` (port 9120) — d'abord, car l'adapter en dépend
2. Adapter (18789) — dépend d'OpenRouter
3. Node Studio (3000) — dépend du .env
4. Tunnel 3000 (cloudflared)
5. Budget (8760) + son tunnel
6. Vaulty (8765) + son tunnel → `bash /root/projets/vaulty/tunnel.sh`
7. Vérifier que tout répond (curl chaque health endpoint)
8. **Présenter les nouvelles URLs** immédiatement

Ne pas demander à l'utilisateur de cliquer des liens d'auth Cloudflare — il n'a pas le temps, il veut que ça marche tout de suite.

## Variantes

### Session CLI vs Gateway
Les sessions CLI ont `source: "cli"`, les sessions cron ont `source: "cron"` avec préfixe `cron_<hash>_<date>`. Filtrer par source si besoin.

### Session vierge / pas de session précédente
Si l'utilisateur démarre un nouveau projet, ignorer ce skill. Aller directement vérifier les fichiers sur disque.