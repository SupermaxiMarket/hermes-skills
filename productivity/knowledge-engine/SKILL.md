---
name: knowledge-engine
description: "Infinite Knowledge Engine léger. Capture → Process → Export → NotebookLM → Insights. 4 fonctions : daily_capture, export_for_notebooklm, generate_daily_summary, meta_review."
category: productivity
---

# Infinite Knowledge Engine v2

Moteur de connaissance personnel minimal et robuste. Pas de Docker, pas de MCP complexe.
**Philosophie** : Hermes fait la recherche, le tool structure et exporte, NotebookLM analyse.

## Structure

```
~/knowledge-engine/
├── vault/
│   └── daily-briefs/       ← daily_capture() stocke ici
├── exports/                ← export_for_notebooklm() stocke ici
├── summaries/              ← generate_daily_summary() stocke ici
└── meta/
    └── reviews.jsonl       ← meta_review() stocke ici
```

## Les 4 fonctions

### 1. `daily_capture(topic, content, source, tags, date)`
Capture une information structurée avec frontmatter YAML dans `vault/daily-briefs/`.
Le fichier est nommé `YYYY-MM-DD_HHMMSS_slug.md`.

**Quand l'utiliser** : Après chaque recherche Hermes, chaque article lu, chaque insight.

**Paramètres** :
- `topic` (obligatoire) : titre de la capture
- `content` : contenu markdown (si vide, template à remplir)
- `source` : URL ou origine
- `tags` : tags séparés par des virgules
- `date` : date YYYY-MM-DD (défaut: aujourd'hui)

### 2. `export_for_notebooklm(date)`
Bundle TOUTES les captures d'une date en un seul fichier `.md` prêt à glisser dans NotebookLM.
Ajoute : header d'import, table des matières, et 5 prompts prêts à copier-coller dans NotebookLM.

**Quand l'utiliser** : En fin de journée, avant d'importer dans NotebookLM.

**5 prompts inclus dans l'export** :
1. Résumé global
2. Insights croisés (thèmes communs, contradictions)
3. Tendances émergentes
4. Questions ouvertes
5. Plan d'action (3 actions concrètes)

### 3. `generate_daily_summary(date)`
Génère un résumé structuré avec 4 sections obligatoires :
1. **Insights clés** — ce que j'ai appris aujourd'hui
2. **Contradictions et tensions** — ce qui s'oppose
3. **Tendances émergentes** — patterns, signaux faibles
4. **Questions ouvertes** — ce qu'il faut creuser

**Quand l'utiliser** : En fin de journée, avant l'export NotebookLM. Template à remplir manuellement.

### 4. `meta_review(date)`
Analyse simple de la journée avec scoring automatique (0-3) :
- ✅ 1 point : captures réalisées
- ✅ 1 point : export NotebookLM généré
- ✅ 1 point : résumé quotidien complété

Produit un rapport : ce qui a marché, ce qu'il faut améliorer. Sauvegardé dans `meta/reviews.jsonl`.

**Quand l'utiliser** : Dernière étape de la journée, après export et summary.

## Workflow quotidien

```bash
# ── MATIN : Capture et Recherche ──
# Hermes fait la recherche, puis :
knowledge_engine daily-capture \
  --topic "DeepSeek V4 bouscule le marché" \
  --source "https://deepseek.com" \
  --tags "ia,llm" \
  --content "DeepSeek V4 : MoE 128K contexte, coût 10x inférieur à GPT-5..."

knowledge_engine daily-capture \
  --topic "NotebookLM analyse du code" \
  --source "https://blog.google" \
  --tags "outils" \
  --content "NotebookLM peut analyser des repos GitHub..."

# ── SOIR : Synthèse ──
knowledge_engine summary      # Génère le template de résumé, à remplir
knowledge_engine export       # Bundle tout pour NotebookLM
knowledge_engine review       # Score et feedback

# ── NOTEBOOKLM : Manuel ──
# 1. Ouvre https://notebooklm.google.com
# 2. Glisse ~/knowledge-engine/exports/notebooklm_export_YYYY-MM-DD.md
# 3. Copie-colle les 5 prompts
# 4. Note les insights dans le résumé
```

## Pièges

- `daily-capture` avec `--content ""` crée un template vide, à remplir manuellement ensuite.
- L'export bundle TOUT le jour. Si tu veux exporter par thème, utilise des dates différentes.
- NotebookLM a une limite d'environ 50 sources par notebook. Si tu dépasses, crée un nouveau notebook.
- Le tool ne fait PAS de recherche web. C'est Hermes qui cherche, le tool qui structure.

## Dépendances

- Python 3.8+ (stdlib uniquement, zéro dépendance externe)
- NotebookLM (Google, gratuit, compte Google requis)
- Hermes Agent (pour la recherche et l'orchestration)

## Intégration Hermes

Le skill est importable dans Hermes :

```python
from knowledge_engine import daily_capture, export_for_notebooklm, generate_daily_summary, meta_review
```

Hermes peut appeler ces fonctions directement après une recherche web, ce qui automatise le flux.