# Narrativ — Implementation Reference

Prototype concret d'une application narrative financière (thriller style).
Construit le 16 septembre 2026 pour Pierre Andre Erard, validé en une itération.

## Concept

**NARRATIV** transforme des données bancaires ennuyeuses en chapitres thriller quotidiens. 
Au lieu de graphiques et de tableaux, l'utilisateur lit "l'histoire de son argent aujourd'hui".

## Stack technique

- **Backend** : Node.js + Express
- **Base** : SQLite (better-sqlite3, WAL mode)
- **Auth** : JWT (PIN 0000 pour MVP monocle)
- **Frontend** : SPA vanilla (HTML + CSS + JS), pas de framework
- **IA** : OpenRouter avec fallback template
- **Déploiement** : Cloudflare tunnel (port 8766)

## Structure du projet

```
/root/projets/narrativ/
├── public/
│   ├── index.html          # SPA (écran login + dashboard + 5 vues)
│   ├── css/style.css       # Thème dark thriller (Crimson Pro + Inter + JetBrains Mono)
│   └── js/
│       ├── api.js          # Client REST (token JWT dans localStorage)
│       └── app.js          # Routing SPA + logique métier
├── server/
│   ├── server.js           # Express, port 8766, SPA catch-all
│   ├── db.js               # SQLite schema (users, accounts, transactions, narratives, goals)
│   ├── .env                # PORT, JWT_SECRET, OPENROUTER_API_KEY, NARRATIVE_DEMO_MODE
│   ├── routes/
│   │   ├── auth.js          # /api/auth/login (PIN), /api/auth/me, /api/auth/settings
│   │   ├── accounts.js      # CRUD comptes bancaires
│   │   ├── transactions.js  # CRUD + import CSV batch
│   │   ├── narratives.js    # /today, /regenerate, history
│   │   ├── goals.js         # CRUD objectifs d'épargne
│   │   └── insights.js      # Dépenses mensuelles, anomalies, catégories
│   └── services/
│       └── narrator.js      # Moteur de narration (template ou AI)
├── data/                    # SQLite DB (auto-créé)
├── package.json
└── launch.sh               # Script de démarrage + tunnel
```

## DB Schema

```sql
CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, 
  created_at TEXT DEFAULT (datetime('now')), settings TEXT DEFAULT '{}');
CREATE TABLE accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
  name TEXT, type TEXT, balance REAL, currency TEXT DEFAULT 'CHF', color TEXT);
CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER, 
  date TEXT, description TEXT, amount REAL, category TEXT, merchant TEXT, notes TEXT);
CREATE TABLE narratives (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
  date TEXT, title TEXT, content TEXT, mood TEXT, insights TEXT DEFAULT '[]');
CREATE TABLE goals (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
  title TEXT, target_amount REAL, current_amount REAL DEFAULT 0, deadline TEXT, status TEXT DEFAULT 'active');
```

## Narrator templates (thriller style)

Le narrateur a 10 titres de chapitres qui tournent :
```
Le Prix de la Liberté, La Tasse de Trop, L'Argent qui Dort, Le Signal d'Alarme,
La Danse des Chiffres, L'Ombre au Portefeuille, La Piste du Mois,
Les Soupçons du Compte, L'Énigme du Budget, Le Silence des Dépenses
```

Chaque narrative suit 7 sections : Hook → Chiffres → Comptes → Top Dépenses → Analyse → Plot Twist → Cliffhanger.

## Mood detection

| Net flow | Mood |
|----------|------|
| > +500 | prosperous 🟢 |
| > 0 | hopeful ✨ |
| > -500 | neutral ⚪ |
| > -2000 | tense 🟡 |
| ≤ -2000 | critical 🔴 |

## Demo data seeding

Le prototype inclut un seeding automatique avec des données suisses réalistes :
- 5 comptes (PostFinance, Crédit Agricole, Trading, Crypto, 3a)
- ~40 transactions sur septembre 2026 (loyer 1450, prime santé 847, Migros, CFF, etc.)
- 3 objectifs d'épargne (Japon 8000, Urgence 10000, Voyage 3000)

## Points d'attention

- **Les salaires sont positifs** (income), pas négatifs. Bien filtrer `t.amount < 0` / `t.amount > 0`
- **Le cache narrative** : /api/narratives/today ne regénère pas si déjà généré pour la journée
- **PIN 0000** : prévu pour démo uniquement, à remplacer par auth complète en prod
- **CSV import** : format attendu `date,description,montant` (une transaction par ligne)
- **Cloudflare tunnel** : l'URL change à chaque restart. Stoppée via `fuser -k 8766/tcp`

## Usage

```bash
cd /root/projets/narrativ
# Kill old
fuser -k 8766/tcp 2>/dev/null
# Start
node server/server.js
# Tunnel
cloudflared tunnel --url http://localhost:8766
```

PIN : 0000
URL locale : http://localhost:8766