---
name: local-web-deployment
description: "Use when user asks to deploy local web app via tunnel."
---

# Local Web Deployment

Use when the user asks to deploy or expose a local web app publicly, or to "put it online", "make it accessible", "start and tunnel".

Worked example: `references/hermes-3d-deployment.md` — full recipe for deploying Hermes3D (Next 16, 3D agent office) with a `hermes serve` JSON-RPC backend, gated Studio (custom /login route) and systemd + cloudflared.

**New architecture (2026-08+)**: `references/hermes3d-adapter-architecture.md` — Hermes3D Studio now connects via the Hermes Gateway Adapter (port 18789, protocole Hermes3D gateway, pas JSON-RPC direct). L'adapter fait le pont entre le Studio 3D et OpenRouter/LLM API. Agent CRUD via WebSocket API documenté.

Cross-browser HTML tips for static sites: `references/cross-browser-html.md` (inputs, storage, encoding, Chart.js pinning, etc.).

File upload in browser-only SPAs: `references/static-spa-file-upload.md` (FileReader → base64 → localStorage, async pitfall, size gating, file viewer in new tab).

Reusable gated-app login route: `templates/login-route.js` — drop-in `/login` for apps protected by STUDIO_ACCESS_TOKEN.

Local HTTP Next.js fixes (CSP + hardcoded WS URLs): `references/local-http-nextjs-pitfalls.md` — ERR_SSL_PROTOCOL_ERROR, page blanche, WebSocket qui échoue sur build hardcodé.

Agent management (création, protection, desk assignments, ajout outils customs): `references/hermes3d-agent-management.md` — créer des agents via l'API WebSocket, les protéger de l'orchestrateur, assigner bureaux, ajouter tools.web_search et tools.news_brief.

News brief cron (script-based, accessible aux agents): `references/hermes3d-news-cron.md` — cron toutes les 6h pour récupérer les news IA/tech, les agents lisent le cache via tools.news_brief.

## Workflow

### 1. Verify project readiness

Always check these before starting:

- Dependencies: check `node_modules` or `venv` exist.
- Environment: check `.env` file exists.
- Database (Prisma/PostgreSQL): run `pg_isready`, check tables exist in `vigilance` DB, check seed data.
- If tables exist but no data → run seed. If tables missing → `npx prisma db push && npm run db:seed`.

### 2. Start the dev server

```bash
cd /root/projets/<project>
npx next dev --port 3000 &   # Next.js projects
```

For **static HTML/JS** (no framework):
```bash
cd /root/projets/<project> && python3 -m http.server 8760 &
```

Wait 10-15s then verify with `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/login` — expect 200 or 307.

### 3. Expose the app

**Preferred: direct WSL IP** — when the user is on the same Windows machine running WSL, tunnels are unnecessary and unreliable. Just bind the server to `0.0.0.0` and give the user:

```
http://<wsl-ip>:<port>
```

Get the WSL IP with `hostname -I` (typically `172.x.x.x`). Say: « C'est en direct, pas de DNS, pas de tunnel. L'IP WSL est accessible depuis Windows sans config. » This is the PRIMARY method for local access; only fall back to a tunnel when the user needs access from outside their LAN.

**Fallback: public tunnel** (use when the user needs public/remote access):

1. **cloudflared** (tested working with HTTP2): `cloudflared tunnel --url http://localhost:3000 --protocol http2 --no-autoupdate`
   The default QUIC transport can crash in a loop on WSL (`failed to run the datagram handler error=context canceled`) → the trycloudflare subdomain stops resolving. HTTP2 is stable.
2. **serveo.net** (often times out): `ssh -o StrictHostKeyChecking=no -R 80:localhost:3000 serveo.net`
3. **localhost.run** (may hang): `ssh -o StrictHostKeyChecking=no -R 80:localhost:3000 nokey@localhost.run`

Extract cloudflared URL: `grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' <log> | tail -1`

### 4. Verify tunnel

```bash
curl -s -o /dev/null -w "%{http_code}" https://<url>.trycloudflare.com/login
```

### 5. Daemonize & save

Use `preexec_fn=os.setsid` (Python) or nohup. Save URL to `/tmp/<project>-url.txt` and update memory.

**Long-lived exposure → systemd user units** (tested 2026-08 on this WSL box):

- App unit MUST carry `EnvironmentFile=/path/to/.env` when the app runs from a plain Node server (`node server/index.js`) or any non-Next CLI. Next's CLI loads `.env` itself, but a bare Node server reads only `process.env` — without EnvironmentFile the gate token, ports, upstream URLs are silently ignored.
- Tunnel unit (cloudflared): `Type=simple` + launcher script that backgrounds cloudflared and `wait "$CF_PID"` → unit stays `active/running`, `Restart=always` works, and the start job does not block. Do NOT use `Type=oneshot` + `RemainAfterExit` with a wait: systemd hangs in `activating/start` and restarts block (`systemctl --user cancel` + reset-failed needed to recover).
- Before (re)starting the tunnel unit, `pkill -f "cloudflared tunnel --url"` first — stale processes hold old URLs and ports and break URL capture.
- Capture the fresh URL from the log: `grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' <log> | head -1` → write to the URL file.

## Pitfalls

- serveo.net: `Connection timed out` to 5.255.123.12:22 — skip to cloudflared.
- **cloudflared QUIC → NXDOMAIN**: the default QUIC transport crashes in a loop (`failed to run the datagram handler error=context canceled`) on this WSL box → DNS stops resolving the trycloudflare subdomain within minutes → browser shows `DNS_PROBE_FINISHED_NXDOMAIN`. Fix: launch with `--protocol http2`:
  `cloudflared tunnel --url http://127.0.0.1:3000 --protocol http2 --no-autoupdate`
  HTTP2 is stable. If the user reports NXDOMAIN, restart the tunnel immediately with `--protocol http2`.
- **Direct WSL IP over tunnel**: Pierre works from Windows → WSL. Tunnels add failure points (DNS, Cloudflare edge). PREFERRED: bind server to `0.0.0.0` and give `http://<wsl-ip>:<port>`. Say: « C'est en direct. » Only tunnel when access is needed outside the LAN.
- cloudflared quick tunnels: ephemeral, URL changes on restart. Warn the user and point them at the URL file rather than a hardcoded URL.
- localhost.run: hangs indefinitely from this WSL env.
- Next 16 Turbopack: first compile ~15s, then fast.
- PrismaPg: uses `/var/run/postgresql` socket + DATABASE_URL env var for migrations.
- Gated apps (STUDIO_ACCESS_TOKEN / cookie auth, e.g. Hermes3D): the shipped access gate often has NO UI to set the cookie → the user hits 401 with no way in. Fix TWO things:
  1. Add a minimal `/login` route (POST form → constant-time compare → `Set-Cookie` → 303 to app) before exposing publicly. Support `?token=` for bookmark/QR deep links. A reusable template is at `templates/login-route.js`.
  2. **Change the access gate to redirect to /login instead of returning raw 401**. In `access-gate.js`, the `handleHttp` function's `else` branch must send a `302` to `/login` instead of a `401 text/plain`. Otherwise the user is stuck — even with a /login route, hitting any protected page (`/office`, `/`) gives a dead-end error. The fix:
     ```
     // Au lieu de:
     res.statusCode = statusCode;
     res.setHeader("Content-Type", "text/plain");
     res.end("Studio access token required...");
     // Faire:
     res.statusCode = 302;
     res.setHeader("Location", "/login");
     res.end();
     ```
- **`.env` non chargé par `node server/index.js`** (critical for Hermes3D et toute app Next déployée avec un serveur Node brut). Le CLI Next (`next dev` / `next start`) charge `.env` automatiquement, mais `node server/index.js` ne lit que `process.env`. Résultat : `STUDIO_ACCESS_TOKEN`, `HOST`, `GATEWAY_URL` sont silencieusement ignorés. Le serveur tourne mais l'access gate est désactivé, le proxy refuse les connexions, etc. Deux solutions :
  - Solution rapide : ajouter un chargeur `.env` en haut de `server/index.js` (voir `references/dotenv-loader.md` pour le code)
  - Solution propre système : `EnvironmentFile=/path/to/.env` dans l'unit systemd
- **Cross-browser HTML**: static HTML/JS apps can look different across browsers. See `references/cross-browser-html.md` for input number → text + inputmode migration, localStorage try/catch for private browsing, multi-byte-safe truncation, full HTML escaping (incl. single quotes), Chart.js version pinning, print color-adjust, and responsive table scroll wrappers.
- **`hermes serve` WebSocket path** (apps using the Hermes JSON-RPC backend): the gateway only accepts WS upgrades on `/api/ws`, NOT on root `/`. The upstream URL in `settings.json` and `.env` (`HERMES3D_GATEWAY_URL`) must be `ws://127.0.0.1:9120/api/ws?token=<SESSION_TOKEN>` — just `ws://127.0.0.1:9120` returns 403/1011. The `?token=` is the dashboard session token (`HERMES_DASHBOARD_SESSION_TOKEN`), distinct from the upstream JSON-RPC auth token (`settings.json`'s `gateway.token` field) — they authenticate different layers (WS upgrade vs JSON-RPC session).
- **`hermes serve --host 0.0.0.0` binds 127.0.0.1 anyway** — depuis le June 2026 hardening, le flag `--host` est ignoré pour les binds non-loopback. Le serve écoute toujours `127.0.0.1`, inaccessible depuis Windows directement. Le frontend Next.js ne doit JAMAIS pointer `ws://<wsl-ip>:9120`. Le proxy Node (port 3000) gère le pont WS entre le navigateur (bind 0.0.0.0) et `hermes serve` (127.0.0.1:9120).
- **Hermes3D Gateway Adapter (port 18789) — NOUVELLE ARCHITECTURE** : le Studio peut aussi se connecter via l'adapter (`server/hermes-gateway-adapter.js`) qui parle le protocole Hermes3D Gateway natif, pas le JSON-RPC. L'adapter translate vers une API LLM OpenAI-compatible (OpenRouter). Dans ce mode, l'URL est simplement `ws://localhost:18789`, pas de path `/api/ws` ni de `?token=`. Les deux architectures co-existent mais ne sont pas interchangeables. Voir `references/hermes3d-adapter-architecture.md`.
- **`UPSTREAM_ALLOWLIST`** (Hermes3D Node proxy): the gateway proxy in `server/gateway-proxy.js` blocks ALL upstream connections if `UPSTREAM_ALLOWLIST` is empty (production default). Set `UPSTREAM_ALLOWLIST=localhost,127.0.0.1` in the Node process's environment (`.env` or systemd unit's `EnvironmentFile`). Without it, the proxy connects but immediately rejects every browser WebSocket with the generic `[gateway-proxy] refusing upstream connection` message.
- **Adapter bind sur 127.0.0.1 par défaut** (Hermes3D Gateway Adapter) : `server/hermes-gateway-adapter.js` hardcode `httpServer.listen(ADAPTER_PORT, "127.0.0.1", ...)`. Quand le proxy Node (port 3000) reçoit une connexion WebSocket depuis le navigateur via tunnel (IP externe) ou via WSL→Windows (172.x.x.x), la connexion upstream vers l'adapter vient d'une IP non-loopback → refusée silencieusement. **Fix** : changer `"127.0.0.1"` en `"0.0.0.0"` dans ce fichier. À refaire après chaque `git pull` car le fichier est versionné.
- **CSP `upgrade-insecure-requests` + HSTS bloquent le HTTP local** (toutes les apps Next.js). Le fichier `next.config.ts` généré par défaut contient `"upgrade-insecure-requests"` dans la directive `Content-Security-Policy` des security headers. Quand l'app est servie en HTTP pur (cas typique WSL→Windows, pas de HTTPS), le navigateur reçoit l'ordre de requêter TOUTE ressource (JS, CSS, fonts) en HTTPS → `ERR_SSL_PROTOCOL_ERROR` sur chaque fichier → page blanche/inutilisable. Le même `next.config.ts` inclut `Strict-Transport-Security: max-age=31536000; includeSubDomains` en production, ce qui aggrave le problème. **Fix** :
  1. Dans `next.config.ts`, retirer `"upgrade-insecure-requests"` de la CSP
  2. Dans `next.config.ts`, supprimer le bloc HSTS (ou le conditionner à un check d'environnement, p.ex. présence d'un certificat HTTPS)
  3. PATCHER AUSSI `.next/routes-manifest.json` — le CSP + HSTS y sont dupliqués en dur. Le navigateur lit depuis ce fichier, pas depuis `next.config.ts` au runtime. Chercher `upgrade-insecure-requests` et `Strict-Transport-Security` dans ce fichier et les retirer.
  4. Après le patch, redémarrer `node server/index.js` (pas besoin de rebuild complet).
- **Build-time hardcoded WebSocket URLs** (Next.js projets, Hermes3D style). Le build Next.js (`next build` ou Turbopack) peut contenir en dur `ws://localhost:<port>` dans les fichiers JS du dossier `.next/static/chunks/` et `.next/server/chunks/`. Quand le browser accède à l'app via une IP différente (WSL: `http://172.x.x.x:3000` au lieu de `http://localhost:3000`), la connexion WebSocket part vers `ws://localhost` → localhost de Windows, pas celui de WSL → échec silencieux. **Diagnostic** : ouvrir F12 → Network → chercher les tentatives WS vers `localhost:18789` ou `127.0.0.1:9120`. **Fix** (voir `references/local-http-nextjs-pitfalls.md` pour les commandes exactes) :
  1. Identifier : `grep -roh 'ws://localhost:[0-9]*' .next/ | sort -u`
  2. Patcher TOUS les fichiers `.js` (pas les `.map`) : remplacer `ws://localhost:18789` par `ws://<wsl-ip>:3000/api/gateway/ws` (le proxy Node, pas l'adapter direct)
  3. Vérifier aussi `ws://127.0.0.1:9120` si présent → idem, remplacer par le proxy
  4. **Ne pas inventer de routes** — le remplacement doit cibler `/api/gateway/ws` qui est déjà monté dans le serveur Node, pas un chemin arbitraire
  5. Redémarrer `node server/index.js` pour prise en compte
- **Ne pas confondre cloudflared (tunnel) avec Cloudflare (DNS/CDN)** — l'utilisateur fait la différence immédiatement. Dire « le tunnel cloudflared » ou simplement « le tunnel » pour l'infrastructure réseau, et « l'accès Studio » / « la page de login » pour l'authentification applicative (STUDIO_ACCESS_TOKEN). Les deux couches sont indépendantes et doivent être expliquées séparément.
- **Modèle LLM inexistant sur OpenRouter** (Hermes3D Gateway Adapter). Le frontend Studio envoie `hermes/deepseek/deepseek-v4-flash:0731-cloud` (préfixe `hermes/` + nom avec `:` et suffixe `-cloud`). OpenRouter a `deepseek/deepseek-v4-flash-0731` (tiret, pas de `-cloud`). L'adapter (`server/hermes-gateway-adapter.js`) a une fonction `resolveHermesModel()` qui split par `/` et prend le dernier segment, mais le `:` et `-cloud` ne sont pas gérés. Résultat : Hermes API HTTP 404. **Fix** : dans `resolveHermesModel()`, ajouter après le `normalized` : `normalized = normalized.replace(/:/g, "-").replace(/-cloud$/i, "");`. Voir `references/hermes3d-adapter-architecture.md` pour le code exact.

## Checklist

- [ ] PostgreSQL accepting connections
- [ ] DB exists with tables
- [ ] Seed data populated
- [ ] node_modules + .prisma generated
- [ ] .env with correct DATABASE_URL
- [ ] Server starts without errors
- [ ] Login page HTTP 200
- [ ] Gated app: /login route exists and sets the access cookie
- [ ] systemd app unit has EnvironmentFile set (plain Node server)
- [ ] Tunnel URL resolves 200
- [ ] URL saved to memory