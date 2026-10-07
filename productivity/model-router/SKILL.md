---
name: model-router
description: Routage intelligent 3 niveaux — DeepSeek V4 Pro / Nemotron 550B / Gemma 4 gratuit
---

# Model Router — Architecture Hybride 3 Niveaux

Système de routage automatique à 3 profils, du plus lourd au plus léger.

| Niveau | Profil | Modèle | Coût | Usage |
|--------|--------|--------|------|-------|
| 💪 | `agent-os-nemotron` | `nvidia/nemotron-3-ultra-550b-a55b:free` | **Gratuit** | Puissance brute, audits, analyse massive |
| 🧠 | `agent-os` | `deepseek/deepseek-v4-pro` | Payant | Planification, création, code complexe |
| ⚡ | `agent-os-fast` | `google/gemma-4-26b-a4b-it:free` | **Gratuit** | Recherche, résumés, exécution rapide |

Inspiré de la mise à jour Gemma 4 (tool calling corrigé) et de la v0.19 Quick Silver.

## 📟 Utilisation

### Wrapper automatique `hm` (recommandé)

```bash
hm "écris un chapitre de thriller"      → 🧠 agent-os
hm "cherche les news IA"               → ⚡ agent-os-fast
hm "audit de sécurité complet"          → 💪 agent-os-nemotron
hm --list                               → Lister les profils
```

Le wrapper analyse la phrase, affiche le modèle choisi + pourquoi, puis lance `hermes --profile X` automatiquement. Installé dans `/usr/local/bin/hm`, alias dans `.bashrc`.

### Routeur manuel

```bash
python ~/.hermes/tools/model_router.py "ta demande"
python ~/.hermes/tools/model_router.py --json "ta demande"
python ~/.hermes/tools/model_router.py --list
```

## 🎯 Règles de routage (ordre de priorité)

### 1. → `agent-os-nemotron` (Nemotron 550B gratuit)
- Audit de sécurité, analyse complète, refactoring lourd
- Projet entier, codebase, revue de code
- Analyse de données massive
- 1M tokens de contexte — idéal pour ingérer un projet complet

### 2. → `agent-os` (DeepSeek V4 Pro)
- Création littéraire (chapitre, roman, fiction)
- Code complexe (architecture, design pattern)
- Décisions stratégiques, debug profond
- Pédagogie détaillée

### 3. → `agent-os-fast` (Gemma 4 gratuit)
- Recherche web, actualités, résumés
- Listes, classements, traduction
- Brainstorming, correction, snippets

### Heuristique par défaut
Aucune règle ne match → `agent-os-fast` (privilégier l'économie).

## 🔧 Architecture

```
Demande utilisateur
        │
        ▼
┌───────────────────┐
│  model_router.py  │
└───────┬───────────┘
        │
   ┌────┼────┐
   ▼    ▼    ▼
Nemotron DeepSeek Gemma 4
(550B)  (planif.) (exécut°)
 gratuit  payant   gratuit
```

## 🔍 Pattern : trouver des alternatives gratuites

Quand un modèle est trop cher, chercher des alternatives gratuites sur OpenRouter :

```bash
curl -s https://openrouter.ai/api/v1/models | \
  python3 -c "import sys,json; [print(m['id'],m.get('context_length',0)) for m in json.load(sys.stdin)['data'] if float(m['pricing']['prompt'])==0]"
```

Puis créer un profil et intégrer au routeur. Voir `references/free-model-hunting.md`.

## 📊 Économie

- **Avant** : tout DeepSeek → coût cumulatif sur tâches simples
- **Maintenant** : 70-90% des tâches sur modèles gratuits (Gemma 4 ou Nemotron)
- **DeepSeek réservé** à la création littéraire et aux décisions complexes
- **Économie estimée** : 60-80% de réduction des coûts API

## ⚙️ Configuration optimale Hermes v0.19+

Paramètres clés activés pour tous les profils :

```bash
hermes config set agent.reasoning_effort max    # Raisonnement poussé
hermes config set display.show_reasoning true   # Réflexion en direct
hermes config set approvals.mode smart          # Approbations intelligentes
```

## 📚 Références

- `references/nemotron-quirks.md` — Comportement, pièges et bonnes pratiques du modèle Nemotron 550B
- `references/free-model-hunting.md` — Méthode pour trouver des modèles gratuits sur OpenRouter