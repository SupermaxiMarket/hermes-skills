# Dotenv loader pour serveur Node brut

`node server/index.js` ne charge PAS `.env` (contrairement à `next dev`/`next start`). Ajoute ce bloc en haut de `server/index.js`, juste après les `require`, pour charger automatiquement `.env.local` puis `.env` :

```javascript
const fs = require("node:fs");
const path = require("node:path");

const loadDotenv = (filePath) => {
  try {
    if (!fs.existsSync(filePath)) return;
    const content = fs.readFileSync(filePath, "utf8");
    for (const line of content.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eq = trimmed.indexOf("=");
      if (eq === -1) continue;
      const key = trimmed.slice(0, eq).trim();
      let val = trimmed.slice(eq + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      if (key && !process.env[key]) process.env[key] = val;
    }
  } catch {}
};
loadDotenv(path.join(__dirname, "..", ".env.local"));
loadDotenv(path.join(__dirname, "..", ".env"));
```

## Ce que ça charge

Toutes les variables du `.env` dans `process.env`, sans écraser les variables déjà définies (ex: env passées par systemd `EnvironmentFile`).

## Appliqué à Hermes3D

Placé dans `server/index.js`, ce loader rend disponibles :

- `STUDIO_ACCESS_TOKEN` → active l'access gate + page de login
- `HOST=0.0.0.0` → bind sur toutes les interfaces (nécessaire pour WSL direct)
- `UPSTREAM_ALLOWLIST` → débloque le proxy gateway
- `HERMES3D_GATEWAY_URL` → URL de l'adapter/backend
- `PORT` → port d'écoute