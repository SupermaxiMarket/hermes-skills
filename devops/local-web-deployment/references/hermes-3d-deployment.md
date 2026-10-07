# Hermes3D — bureau 3D des agents (déploiement complet, 2026-08)

Hermes3D (github.com/iamlukethedev/Hermes3D) est un frontend Next 16 qui visualise les agents Hermes dans un office 3D. Déployé pour Pierre à `~/projets/hermes-3d`, port 3000, backend JSON-RPC `hermes serve` port 9120, tunnel cloudflared public.

Architecture du branchement (choisie : liaison directe, PAS l'adapter HTTP) :

```
Browser <-> Studio server (:3000) <-> bridge JSON-RPC in-process <-> hermes serve (:9120, loopback)
```

## Étape 1 — Backend hermes serve

`hermes serve` expose le gateway JSON-RPC (/api/ws, JSON-RPC 2.0) utilisé par le desktop app et les clients distants.

- Ne PAS réutiliser `HERMES_DASHBOARD_SESSION_TOKEN` comme secret partagé : Hermes charge `~/.hermes/.env` avec override=True et le pin casserait le token du desktop app. Créer un nom dédié :
  `echo "HERMES3D_OFFICE_TOKEN=$(openssl rand -hex 32)" >> ~/.hermes/.env`
- Lancer :
  `HERMES_DASHBOARD_SESSION_TOKEN="$(grep '^HERMES3D_OFFICE_TOKEN=' ~/.hermes/.env | cut -d= -f2)" hermes serve --host 127.0.0.1 --port 9120 --skip-build`
- Loopback = auth par token sur query string. Bind public (non-loopback) = login gate à ticket unique, non supporté par le client Hermes3D. Toujours 127.0.0.1 + tunnel.
- `--skip-build` évite le build web inutile (serve est headless).
- Vérif : `curl -s -H 'Host: localhost' http://127.0.0.1:9120/api/status` → JSON avec `gateway_running:true`.

## Étape 2 — Fichier settings Studio

Le serveur Studio lit `~/.hermes/hermes3d/settings.json` pour auto-connecter le backend (référencé par `server/studio-settings.js`, clé `gateway`). Pré-écrire la config connectée plutôt que dépendre d'un clic UI :

```json
{
  "version": 1,
  "gateway": {
    "url": "ws://127.0.0.1:9120/api/ws?token=<HERMES_DASHBOARD_SESSION_TOKEN>",
    "token": "<HERMES3D_OFFICE_TOKEN>",
    "adapterType": "hermes"
  }
}
```

⚠️ **Deux tokens distincts** :
- Le `?token=` dans l'URL = `HERMES_DASHBOARD_SESSION_TOKEN` (auth WS upgrade, celui passé à `hermes serve --port 9120`)
- Le `gateway.token` dans le JSON = `HERMES3D_OFFICE_TOKEN` (auth JSON-RPC session, injecté dans le connect frame)

⚠️ **Path obligatoire** : le serve `hermes` sur port 9120 n'accepte les WebSocket QUE sur `/api/ws`, pas sur `/`. L'URL doit être `ws://127.0.0.1:9120/api/ws?token=...` — PAS juste `ws://127.0.0.1:9120`.

- `adapterType: "hermes"` = bridge JSON-RPC direct.
- `adapterType: "hermes-agent"` = adapter HTTP legacy.

Autres valeurs : `demo`, `custom`.

Ne PAS oublier le champ `"version": 1` dans settings.json, sinon le Studio ignore le fichier.

## Étape 3 — .env du projet

- `NEXT_PUBLIC_GATEWAY_URL` / `HERMES3D_GATEWAY_URL=ws://127.0.0.1:9120`
- `HERMES3D_GATEWAY_TOKEN=<HERMES3D_OFFICE_TOKEN>`
- `HERMES3D_GATEWAY_ADAPTER_TYPE=hermes-agent`
- `STUDIO_ACCESS_TOKEN=<openssl rand -hex 24>` — obligatoire si bind public (network-policy.js refuse 0.0.0.0 sans lui).
- `PORT=3000`, `HOST=0.0.0.0`, `DEBUG=false`

PITFALL MAJEUR : `server/index.js` NE charge PAS `.env` en prod (seul le CLI Next le fait via `next build`/`next dev`). Un `node server/index.js` lit uniquement `process.env` → dans l'unit systemd, `EnvironmentFile=/root/projets/hermes-3d/.env` est obligatoire sinon STUDIO_ACCESS_TOKEN/HOST/GATEWAY sont silencieusement ignorés.

## Étape 4 — Accès gate + login

`STUDIO_ACCESS_TOKEN` déclenche un access gate (server/access-gate.js) : 401 sur HTTP + rejet WebSocket sans cookie `studio_access`. L'app d'origine n'a AUCUNE UI pour poser ce cookie → trou pour l'utilisateur.

Ajout maison : `server/login-route.js` branché dans `createServer()` de `server/index.js` avant `accessGate.handleHttp` :
- `GET /login` → page HTML (form stylé).
- `POST /login` (token) ou `GET /login?token=...` → comparatif constant-time → `Set-Cookie: studio_access=...; HttpOnly; SameSite=Lax; Max-Age=1209600` → 303 `/office`.
- Rate-limit 10 tentatives/min géré par access-gate lui-même.

## Étape 5 — UPSTREAM_ALLOWLIST (proxy Node)

Le proxy gateway dans `server/gateway-proxy.js` vérifie la variable d'env `UPSTREAM_ALLOWLIST` en production. Si elle est absente ou vide, TOUTE connexion WebSocket est refusée avec :

```
[gateway-proxy] refusing upstream connection: UPSTREAM_ALLOWLIST is empty in production.
```

Ajouter dans le `.env` du projet (ou dans l'`EnvironmentFile` de l'unit systemd) :

```
UPSTREAM_ALLOWLIST=localhost,127.0.0.1
```

## Étape 6 — Services systemd (user)

- `hermes3d-serve.service` : `EnvironmentFile=/root/.hermes/.env` + ExecStart = la commande de l'étape 1 en /bin/sh -c (relit le token).
- `hermes3d-office.service` : `WorkingDirectory=/root/projets/hermes-3d`, `EnvironmentFile=/root/projets/hermes-3d/.env`, `ExecStart=/root/.local/bin/npm start`.
- `hermes3d-tunnel.service` : Type=simple, script qui background cloudflared, grep l'URL, `wait $CF_PID` (voir le SKILL.md local-web-deployment pour le pattern et l'écueil oneshot).

## Vérification de bout en bout

1. `systemctl --user is-active hermes3d-serve hermes3d-office hermes3d-tunnel` → actives.
2. `curl http://127.0.0.1:3000/api/health` → `{"ok":true}`.
3. WebSocket test (depuis ~/projets/hermes-3d pour résoudre `ws`) :
   `node -e "const W=require('ws');const w=new W('ws://127.0.0.1:9120/api/ws?token=<TOKEN>');w.on('open',()=>{console.log('OPEN');process.exit(0)});w.on('error',e=>{console.log(e.message);process.exit(1)});setTimeout(()=>process.exit(2),5000)"` → OPEN (note: le path `/api/ws?token=` est obligatoire).
4. Public : `/login` 200, `/office` 401 sans cookie, 200 avec.

## État actuel (2026-08-26)

- Services actifs + enabled, URL courante dans `/tmp/hermes3d-url.txt` (change à chaque restart tunnel).
- Studio token : `HERMES3D_STUDIO_TOKEN` dans `~/.hermes/.env`.
- Le port 3000 appartient désormais à Hermes3D — ne pas y relancer Vigilance sans changer de port.
- Le tunnel quick est éphémère : une URL stable nécessite un tunnel nommé + domaine Cloudflare.