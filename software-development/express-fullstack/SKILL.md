---
name: express-fullstack
description: Build full-stack Express+SQLite+JWT apps rapidly.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [express, nodejs, sqlite, fullstack, jwt, stripe, api, backend]
---

# Express Full-Stack Builder

Construire une application web complète avec backend Express, base SQLite, authentification JWT, paiements Stripe, i18n, et frontend statique servi par Express.

## Architecture standard

```
projet/
├── index.html              # Frontend SPA (servi par Express)
├── styles.css              # Styles
├── app.js                  # Frontend logic
├── i18n.js                 # Traductions (5 langues)
├── server/
│   ├── server.js           # Point d'entrée Express
│   ├── db.js               # SQLite (better-sqlite3)
│   ├── auth.js             # JWT middleware
│   ├── .env                # Config
│   ├── routes/             # auth.js, api.js, stripe.js
│   └── data/               # SQLite DB (auto-créé)
└── package.json
```

## Workflow

### 1. Idéation & Design
Brainstormer le concept, définir le freemium (5/3/3 limits), choisir un design system, prévoir 5 langues.

### 2. Frontend statique (SPA)
`index.html` (landing + auth + app) + `styles.css` (variables CSS) + `app.js` (logique) + `i18n.js` (traductions).

### 3. Backend Express
`npm init -y && npm install express better-sqlite3 jsonwebtoken bcryptjs cors helmet express-rate-limit dotenv stripe`

### 4. DB Schema (SQLite WAL)
Tables : users (name, email, password, plan, lang, theme, stripe_*), documents, warranties, subscriptions. Foreign keys cascade delete.

### 5. Auth (JWT)
bcrypt hash → `generateToken()` → 30d expiry. Middleware `authMiddleware` + `requirePremium`. Token contient `{id, email, plan}`.

### 6. API CRUD
Vérifier les limites du plan gratuit avant chaque création. Renvoyer `{ error, code: 'UPGRADE_NEEDED' }` si dépassé.

### 7. Stripe
`POST /api/stripe/create-checkout` → session CHF. Webhook `checkout.session.completed` + `customer.subscription.deleted`. Mode démo si pas de clé.

### 8. Déploiement
`node server/server.js` → `cloudflared tunnel --url http://localhost:<port>`.

## SPA catch-all (critical)

NE PAS utiliser `app.get('*', ...)` — Express lève une erreur si placé après les routes API.

**Correct :**
```javascript
// Static files INDIVIDUELLEMENT (pas index.html)
app.use('/styles.css', express.static(path.join(__dirname, '..', 'styles.css')));
app.use('/app.js', express.static(path.join(__dirname, '..', 'app.js')));
app.use('/i18n.js', express.static(path.join(__dirname, '..', 'i18n.js')));

// Routes API
app.use('/api/auth', rateLimiter, require('./routes/auth'));
app.use('/api', rateLimiter, require('./routes/api'));
app.use('/api/stripe', require('./routes/stripe'));

// SPA fallback — app.use pas app.get
app.use((req, res) => res.sendFile(path.join(__dirname, '..', 'index.html')));
```

## Freemium model

| Limite | Gratuit | Premium |
|--------|---------|---------|
| Documents | 5 | Illimité |
| Garanties | 3 | Illimité |
| Abonnements | 3 | Illimité |
| Prix | CHF 0 | CHF 9.90/mois ou 99/an |

## Stripe demo mode

Si `STRIPE_SECRET_KEY` contient "placeholder", l'upgrade UI se fait en local avec confetti. Le webhook `checkout.session.completed` met à jour `users.plan` en DB.

## Social meta tags

```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:type" content="website">
<meta property="og:url" content="...">
<meta property="og:image" content="...">
<meta property="og:locale" content="fr_CH">
<meta name="twitter:card" content="summary_large_image">
```

## Pièges

- `app.get('*')` en dernier plante sur les 404 API → utiliser `app.use()` catch-all
- Stripe webhook nécessite `express.raw()`, PAS `express.json()` sur cette route
- Base64 ~1.37× la taille fichier → `limit: '50mb'` dans `express.json()`
- Ne PAS servir `index.html` via `express.static()` → casse le SPA routing
- Toujours `fuser -k <port>/tcp` avant de lancer le serveur
- URL cloudflared change à chaque restart → stocker dans `/tmp/<projet>-url.txt`

## Voir aussi

- `narrative-web-app` — ajouter une narration IA aux données utilisateur (finances, santé, journal)
- `local-web-deployment` — tunnels et déploiement
- `claude-design` — design UI/UX
- `creative-ideation` — brainstorming