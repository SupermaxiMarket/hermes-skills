---
name: narrative-web-app
description: "Use when building web apps with AI narrative from user data."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
tags: [narrative, storytelling, AI, express, nodejs, narrative-finance, thriller]
related_skills: [express-fullstack, creative-ideation, humanizer]
---

# Narrative Web App Builder

Construire des applications web où l'expérience centrale est un récit généré par IA à partir des données structurées de l'utilisateur. Pas un dashboard — une histoire.

## Architecture type

```
projet/
├── public/
│   ├── index.html          # SPA sombre, immersive, type "lecture"
│   ├── css/style.css       # Theme dark typographique (serif + mono)
│   └── js/
│       ├── api.js          # Client API
│       └── app.js          # SPA routing + affichage narratif
├── server/
│   ├── server.js           # Express entry point
│   ├── db.js               # SQLite schema
│   ├── .env                # Configuration
│   ├── routes/
│   │   ├── auth.js         # JWT simple (PIN pour MVP)
│   │   ├── narrative.js    # Génération du récit
│   │   ├── data.js         # CRUD sur les données source
│   │   └── insights.js     # Statistiques + anomalies
│   └── services/
│       └── narrator.js     # Moteur de narration (template ou AI)
├── data/                   # SQLite DB
└── package.json
```

## Workflow

### 1. Définir le domaine et la voix narrative
- Quel type de données ? (finances, santé, productivité, journal)
- Quelle voix narrative ? (thriller — conseiller — poétique — épistolaire)
- Le style doit matcher l'audience : Pierre utilise le thriller car son public true crime aime le suspense

### 2. Modèle de données
- Tables pour les données source (ex: comptes, transactions, objectifs)
- Table pour les récits générés (date, titre, contenu, mood, insights)
- Les données source doivent pouvoir être importées (CSV, API, saisie manuelle)

### 3. Moteur de narration (narrator.js)

Deux modes, avec fallback automatique :

**Mode template (démo, sans clé API) :**
```javascript
function generateNarrative(data) {
  const parts = [];
  parts.push(`# ${titles[day % titles.length]}`);
  parts.push(`**Revenus :** ${monthlyIncome} CHF. **Dépenses :** ${monthlySpend} CHF.`);
  topExpenses.slice(0, 3).forEach((tx, i) => {
    parts.push(`${i+1}. ${tx.description} (${Math.abs(tx.amount)} CHF)`);
  });
  parts.push(plotTwists[day % plotTwists.length]);
  parts.push(closings[day % closings.length]);
  return parts.join('\n');
}
```

**Mode AI (OpenRouter) :**
```javascript
async function generateAINarrative(data) {
  const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: process.env.OPENROUTER_MODEL || 'deepseek-v4-flash:0731-cloud',
      messages: [
        { role: 'system', content: 'Tu es le narrateur. Style thriller, phrases courtes, tension.' },
        { role: 'user', content: prompt }
      ],
      max_tokens: 1024,
      temperature: 0.8,
    }),
  });
  const json = await response.json();
  return json.choices[0].message.content;
}
```

### 4. Routes narratives

```javascript
// GET /api/narratives/today — get or create today's narrative
router.get('/today', (req, res) => {
  const today = new Date().toISOString().split('T')[0];
  let narrative = db.prepare('SELECT * FROM narratives WHERE user_id = ? AND date = ?').get(userId, today);
  if (!narrative) {
    const data = prepareNarrativeData(userId);
    const content = generateNarrative(data);
    // insert + return
  }
  res.json({ narrative });
});

// POST /api/narratives/regenerate — force regen
router.post('/regenerate', (req, res) => {
  db.prepare('DELETE FROM narratives WHERE user_id = ? AND date = ?').run(userId, today);
  // regenerate + return
});
```

### 5. Frontend narratif
- Afficher le récit dans une carte sombre (padding large, police serif pour le titre, monospace pour les chiffres)
- Mood indicator (emoji + couleur : 🟢 prospère, 🟡 tendu, 🔴 critique)
- Bouton "Réécrire" qui appelle `/api/narratives/regenerate`
- Navigation entre le récit, les données source, et les insights
- Le chargement montre un spinner avec "Le narrateur écrit ton chapitre..."

### 6. Insights & Anomalies
- Comparaison mois courant / mois précédent / année précédente
- Détection des anomalies : transactions > 3× la moyenne
- Catégorie dominante du mois

## Structure narrative thriller (style Pierre)

```
# Le Prix de la Liberté
*dimanche, 20 septembre 2026*

[Hook] — une phrase choc sur le solde ou une dépense.
[Les chiffres] — faits bruts : revenus, dépenses, flux net.
[Les comptes] — snapshot de chaque compte avec son état.
[Les dépenses qui parlent] — top 3 dépenses du mois.
[Analyse] — la catégorie qui domine, présentée comme un point faible.
[Les objectifs] — progression sur les objectifs d'épargne.
[Plot twist] — révélation sur un coût caché ou opportunité.
[Cliffhanger] — phrase de fin qui donne envie de revenir demain.
```

## Mood detection

```javascript
function detectMood(data) {
  const netFlow = data.netFlow || 0;
  if (netFlow > 500) return 'prosperous';
  if (netFlow > 0) return 'hopeful';
  if (netFlow > -500) return 'neutral';
  if (netFlow > -2000) return 'tense';
  return 'critical';
}
```

## Pitfalls

- **Le mode template doit produire un texte crédible même sans API** — tester avec `NARRATIVE_DEMO_MODE=true` avant d'ajouter l'IA
- **Cache quotidien** : une narrative générée est stockée en DB pour la journée. Ne pas la régénérer à chaque requête
- **Salaires ≠ dépenses** : bien filtrer `t.amount < 0` pour les dépenses, `t.amount > 0` pour les revenus
- **Validation utilisateur** : Pierre a validé le concept Narrativ (thriller + finances) en une itération — builder vite, ne pas sur-analyser
- **Cloudflare tunnel** : l'URL change à chaque restart. Stocker dans `/tmp/narrativ-url.txt`

## Voir aussi

- `express-fullstack` — la base Express+SQLite+JWT
- `references/narrativ-implementation.md` — implémentation concrète du prototype Narrativ
- `creative-ideation` — brainstorming de concepts
- `humanizer` — ajustement de ton pour la voix narrative