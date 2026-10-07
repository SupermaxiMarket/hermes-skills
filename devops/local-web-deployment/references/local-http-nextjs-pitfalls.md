# Local HTTP Next.js Pitfalls: CSP + Hardcoded WS URLs

## Symptômes

1. **`ERR_SSL_PROTOCOL_ERROR`** sur toutes les ressources JS, CSS, fonts
2. **Page blanche** / app inutilisable dans le navigateur
3. **WebSocket ne se connecte pas** — `ws://localhost:18789` ou `ws://127.0.0.1:9120` échoue

## Cause 1 : CSP `upgrade-insecure-requests`

Le fichier `next.config.ts` généré par défaut inclut `"upgrade-insecure-requests"` dans la CSP.
Quand l'app est servie en HTTP (WSL vers Windows), le navigateur force le HTTPS pour chaque
sous-ressource → toutes les requêtes échouent.

Le même fichier ajoute `Strict-Transport-Security: max-age=31536000; includeSubDomains`
en mode production → même problème, en pire (le navigateur peut retenir la directive HSTS
lors de sessions ultérieures).

### Fichiers à patcher

| Fichier | Quoi retirer | Pourquoi |
|---------|-------------|----------|
| `next.config.ts` | `"upgrade-insecure-requests"` de la CSP | Source originale |
| `next.config.ts` | Le bloc `Strict-Transport-Security` entier (ou `max-age=0`) | HSTS n'a pas de sens en HTTP local |
| `.next/routes-manifest.json` | `"upgrade-insecure-requests"` dans la CSP | Cache du build — le navigateur lit depuis ici |
| `.next/routes-manifest.json` | `Strict-Transport-Security` header | Idem |

### Commande de vérification

```bash
curl -s -D - http://localhost:3000/office | grep -E 'Content-Security|Strict-Transport'
```

### Notes

- `upgrade-insecure-requests` est utile en prod derrière un reverse proxy HTTPS (Caddy, nginx).
- En local WSL, il est TOUJOURS à retirer.
- Le redémarrage de `node server/index.js` suffit — pas besoin de rebuild Next.

## Cause 2 : WebSocket URLs hardcodées dans le build

Le build Next.js (`.next/static/chunks/*.js` et `.next/server/chunks/*.js`) peut contenir
en dur `ws://localhost:18789` ou `ws://127.0.0.1:9120`. Quand le navigateur accède à l'app
via l'IP WSL (`http://172.x.x.x:3000`), les WebSocket tentent de se connecter à
`ws://localhost` qui est le localhost de Windows → échec.

### Diagnostic

```bash
# Vérifier les URLs WS dans le build
grep -roh 'ws://[a-zA-Z0-9.:/-]*' .next/static/ | sort -u

# Vérifier les fichiers concernés
grep -rl 'ws://localhost:18789' .next/ | grep -v '.map'
grep -rl 'ws://127.0.0.1:9120' .next/ | grep -v '.map'
```

### Fichiers à patcher (typiquement)

```
.next/static/chunks/21f29599a2f7a5cd.js
.next/static/chunks/aa2b7480f56f5a93.js
.next/server/chunks/ssr/[root-of-the-server]__e613158d._.js
.next/server/chunks/ssr/src_lib_7bc2ea82._.js
.next/server/chunks/src_lib_studio_settings-store_ts_6b8813cf._.js
```

### Remplacement

```bash
# Remplacer localhost:18789 par le proxy Node
find .next/ -name '*.js' -not -name '*.map' -exec sed -i \
  's|ws://localhost:18789|ws://172.17.x.x:3000/api/gateway/ws|g' {} \;

# Remplacer aussi 127.0.0.1:9120 si présent
find .next/ -name '*.js' -not -name '*.map' -exec sed -i \
  's|ws://127.0.0.1:9120|ws://172.17.x.x:3000/api/gateway/ws|g' {} \;
```

**Important** : la cible DOIT être le proxy Node (`/api/gateway/ws`) pas l'adapter direct
(`localhost:18789`). Le proxy gère l'authentification (cookie `studio_access`) et le
routage. L'adapter direct ne parle pas le même protocole et ne gère pas le cookie.

### Vérification

```bash
# Depuis WSL — tester que le proxy WS fonctionne
node -e '
const WebSocket = require("ws");
const ws = new WebSocket("ws://127.0.0.1:3000/api/gateway/ws",
  {headers: {Cookie: "studio_access=TOKEN"}});
ws.on("message", d => {
  const m = JSON.parse(d);
  if (m.event === "connect.challenge")
    ws.send(JSON.stringify({type:"req",method:"connect",id:"1",params:{auth:{deviceToken:"test"},version:"1.0"}}));
  if (m.ok) { console.log("GATEWAY OK"); ws.close(); }
});
'
```

## Erreurs typiques (F12 → Console)

```
ERR_SSL_PROTOCOL_ERROR              → CSP upgrade-insecure-requests
ERR_CONNECTION_REFUSED (WS)         → URL hardcodée vers localhost Windows
WebSocket connection to 'ws://...' failed → voir les deux ci-dessus
Unsafe attempt to load URL https://... → CSP/HSTS force HTTPS
```

## Ordre de correction recommandé

1. Patcher `next.config.ts` (CSP + HSTS)
2. Patcher `.next/routes-manifest.json`
3. Patcher les builds `.next/static/chunks/` et `.next/server/chunks/`
4. Redémarrer `node server/index.js`
5. F5 dans le navigateur
6. Vérifier F12 → Network → pas d'erreur rouge
7. Vérifier F12 → Console → WebSocket connecté