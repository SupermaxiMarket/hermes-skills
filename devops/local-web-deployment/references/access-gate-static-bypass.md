# Access gate public path bypass pour Next.js gated apps

## Contexte

Quand Hermes3D (ou toute app Next.js) est protégée par `STUDIO_ACCESS_TOKEN`,
l'access gate intercepte TOUTES les requêtes HTTP, y compris les fichiers
statiques dans `public/`. Résultat : un fichier dans `public/budget/index.html`
renvoie 401 au lieu d'être accessible publiquement.

## Solution

Patcher `server/index.js` pour que certains chemins court-circuitent le gate :

```js
  const createServer = () =>
    useHttps
      ? https.createServer(httpsCert, (req, res) => {
          handleLogin(req, res, process.env.STUDIO_ACCESS_TOKEN).then(
            (handled) => {
              if (handled) return;
              const pn = (req.url || '/').split('?')[0];
              if (pn.startsWith('/budget') || pn === '/') {
                handle(req, res);
                return;
              }
              if (accessGate.handleHttp(req, res)) return;
              handle(req, res);
            },
            () => {
              const pn = (req.url || '/').split('?')[0];
              if (pn.startsWith('/budget') || pn === '/') {
                handle(req, res);
                return;
              }
              if (accessGate.handleHttp(req, res)) return;
              handle(req, res);
            }
          );
        })
      : http.createServer((req, res) => {
          // même pattern
        });
```

Les deux branches (HTTPS et HTTP) doivent être patchées identiquement.
Les chemins publics doivent être listés explicitement — ne pas ouvrir tout `/`.

## Fichiers statiques via Next.js public/

Placer les fichiers dans `~/hermes-3d/public/<sous-chemin>/` → Next.js les
sert à `/sous-chemin/`. Pas de rebuild nécessaire, pas de redémarrage.

## Service systemd

L'app unit doit avoir `EnvironmentFile=/path/to/.env` pour que les vars
soient visibles du serveur Node (Next.js CLI les charge, mais `node server/index.js`
ne le fait pas).