---
name: meta-reviewer
description: Analyse post-tâche automatique. Évalue les performances et propose des améliorations concrètes (skills, prompts, routing, config).
---

# Meta Reviewer

Analyse les performances après chaque tâche complexe (5+ étapes) et propose des améliorations.

## Script exécutable

Le script `meta_review.py` est installé :
- Script : `~/.hermes/tools/meta_review.py`
- Alias  : `metareview` (lié dans `/usr/local/bin/metareview`)
- Données: `~/.hermes/meta_reviews.json`
- Rapports: `~/.hermes/meta_reviews/YYYY-MM-DD_<session>.md`

## Commandes CLI

```bash
metareview analyze                  # Analyser la dernière session disponible
metareview analyze --session <id>  # Analyser une session spécifique
metareview report                  # Rapport complet + sauvegarde Markdown
metareview auto                    # Raccourci: analyse + rapport
metareview stats                   # Statistiques globales (scores, modèles, patterns)
metareview patterns                # Patterns d'échec récurrents
metareview suggest                 # Suggestions d'amélioration
metareview list                    # Lister les reviews sauvegardées
metareview show <fichier>          # Afficher une review spécifique
```

## Déclencheurs

Le Meta Reviewer s'active automatiquement quand :
1. Une tâche a nécessité **5+ tool calls**
2. Une tâche a connu **au moins 1 erreur/réessai**
3. L'utilisateur dit **"Review"**, **"Analyse ça"**, ou **"Meta"**
4. Un skill existant a été utilisé et s'est révélé incomplet

## Système de scoring (0-100)

| Critère | Poids | Description |
|---------|-------|-------------|
| erreurs | -5 / erreur (max -30) | Pénalité par erreur détectée |
| retries | -4 / retry (max -20) | Pénalité par retry/bottleneck |
| productivité | +15 max | Bonus si tool_calls > 5 et fichiers modifiés |
| autonomie | +10 max | Bonus si 0 erreur ET 0 retry avec task active |
| lenteur | -10 | Pénalité si durée > 10min pour peu de résultats |

### Grades

| Score | Grade | Signification |
|-------|-------|---------------|
| 95-100 | S | Exceptionnel — aucune amélioration nécessaire |
| 85-94  | A | Très bien — quelques optimisations mineures |
| 70-84  | B | Bien — améliorations identifiées |
| 55-69  | C | Moyen — problèmes significatifs |
| 40-54  | D | Faible — refonte de l'approche nécessaire |
| 0-39   | F | Échec — analyse approfondie requise |

## Patterns d'échec détectés

| Pattern | Sévérité | Déclencheur | Suggestion |
|---------|----------|-------------|------------|
| high_error_rate | high | 3+ erreurs | Vérifier permissions, chemins, timeouts |
| high_retry_rate | medium | 3+ retries | Changer de méthode après 2 échecs |
| no_deliverable | medium | >15min sans fichier | Découper en sous-tâches |
| low_efficiency | medium | 20+ tool calls, <2 fichiers | Utiliser execute_code pour batch |
| regression | high | Erreurs > 2x la moyenne | Revoir changements récents |

## Catégories de suggestions

- **pattern** : Correction de patterns d'échec détectés
- **skill** : Utilisation d'un skill existant non utilisé
- **soul.md** : Mise à jour de SOUL.md / personnalité
- **new_skill** : Création d'un nouveau skill nécessaire

## Processus d'analyse

### 1. Collecte des métriques

Pour la tâche qui vient de s'achever, collecter :

```
- Nombre de tool calls : 12
- Erreurs rencontrées : 2 (permission denied, model hallucination)
- Réessais : 1
- Durée estimée : ~3 min
- Skills utilisés : daily_ai_brief, project-manager
- Fichiers modifiés : 5
- Échecs partiels : 1 (PDF emoji stripping)
```

### 2. Diagnostic

Pour chaque problème identifié, classer en :

| Catégorie | Exemple |
|-----------|---------|
| **Skill manquant** | Aucun skill pour gérer les PDF avec emojis |
| **Skill obsolète** | daily_ai_brief ne documente pas le fallback Gemini |
| **Prompt faible** | La personnalité "pierre" manque de contexte sur X |
| **Routing** | Tâche simple routée sur DeepSeek au lieu de Gemini Flash |
| **Config** | Timeout trop court pour les recherches web |
| **Process** | Trop de confirmations manuelles demandées |

### 3. Recommandations

Pour chaque problème, une action concrète :

```
Problème : PDF échoue avec emojis (connu, déjà dans la mémoire)
Action : Le skill daily_ai_brief documente déjà le stripping.
   → Vérifier que la règle est appliquée dans generate_pdf.py
   → À faire : ajouter un pre-check dans le script

Problème : 2 tool calls inutiles (ls + cat au lieu de search_files + read_file)
Action : Créer un mini-skill "file-ops-best-practices"
   → ou ajouter une règle dans SOUL.md
```

### 4. Rapport

Format de sortie :

```
META REVIEW — [Agent OS] "Créer le Daily AI Brief v2"

Métriques : 8 tool calls | 1 erreur | 0 réessai | 4 min

Ce qui a bien fonctionné :
  - Recherche multi-source parallèle
  - Fallback Telegram → sauvegarde locale

Améliorations possibles :
  1. [Config] Timeout web_search trop court → 30s → 60s
  2. [Skill] daily_ai_brief manque un exemple de fallback visuel
  3. [Prompt] La personnalité pierre pourrait mentionner les PDFs

Actions suggérées :
  - Patch daily_ai_brief : ajouter section "Exemples visuels"
  - Patch config.yaml : web.timeout = 60
  - Créer skill "pdf-troubleshooting" ? (oui/non)

Score d'efficacité : 85/100 (+5 vs moyenne)
```

## Intégration avec les autres skills

### → Kanban Manager
Après une Meta Review, les actions suggérées sont automatiquement ajoutées en TODO dans le kanban :
```
Kanban + [Meta] Patch daily_ai_brief : ajouter exemples visuels
Kanban + [Meta] Augmenter web.timeout à 60s
```

### → Project Manager
Le rapport est sauvegardé dans `~/.hermes/meta_reviews/YYYY-MM-DD_<session>.md`

### → Model Router
Les métriques de performance par modèle sont traquées :
```
deepseek/deepseek-v4-pro : 12 tâches | 85% efficacité | 2.3 erreurs/tâche
google/gemini-2.5-flash  : 3 tâches  | 92% efficacité | 0.7 erreurs/tâche
```

## Base de connaissances

Les leçons apprises alimentent automatiquement :
- **Mémoire** : faits importants (ex: "PDF emoji non supporté par DejaVu")
- **Skills** : nouvelles procédures découvertes
- **SOUL.md** : ajustements de personnalité et standards

## Technique : Parsing des sessions JSONL

Les fichiers de session sont au format JSONL dans `~/.hermes/sessions/`.
Chaque ligne est un objet JSON avec un champ `role` (user/assistant/tool).

Pour compter les tool calls réels :
- Parser chaque ligne JSON, compter les entrées `tool_calls` dans les messages `assistant`
- Pour les erreurs : vérifier le champ `error` dans les messages `role: "tool"` — ignorer `"error": null` (réponse normale)
- Ne PAS faire de grep brut sur le contenu (faux positifs massifs avec `"error": null` dans chaque réponse d'outil)

## Exemple concret

```
Toi →   Review
Moi →   META REVIEW — Session du 22 mai 2026

        Session : 34 tool calls | 2 erreurs | 1 réessai | 15 min actives

        Points forts :
          - Création fluide de 3 skills (kanban, daily-brief v2, meta-reviewer)
          - Aucune confirmation inutile demandée
          - Fichiers bien structurés

        Améliorations :
          1. [Skill] project-manager manque l'intégration kanban → patch prévu
          2. [Config] display.show_reasoning = false (actif inutilement)
          3. [Process] 2 tool calls redondants (ls puis search_files)

        Score : 88/100
```
