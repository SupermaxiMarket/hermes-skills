# Free Model Hunting — Trouver des alternatives gratuites aux modèles chers

## Contexte

Quand Pierre veut accéder à un modèle premium (ex: Claude Opus 5) sans payer, on exploite
le catalogue OpenRouter pour trouver des alternatives gratuites ou quasi-gratuites.

## Méthode

### 1. Lister tous les modèles gratuits

```bash
curl -s https://openrouter.ai/api/v1/models | python3 -c "
import sys, json
data = json.load(sys.stdin)['data']
free = [m for m in data if float(m['pricing']['prompt']) == 0]
free.sort(key=lambda m: m.get('context_length', 0), reverse=True)
for m in free:
    print(f\"{m['id']:<55} ctx={m.get('context_length',0):>7}  {m.get('description','')[:80]}\")
"
```

### 2. Critères de sélection

- **Taille du modèle** : privilégier les gros (>100B) pour les tâches lourdes
- **Contexte** : 1M tokens = peut ingérer un projet entier
- **Fournisseur** : NVIDIA, Google, Meta → modèles éprouvés
- **Nom évocateur** : "ultra", "pro", "super" → souvent les plus performants

### 3. Créer un profil Hermes

```bash
hermes profile create agent-os-<nom>
# Éditer ~/.hermes/profiles/agent-os-<nom>/config.yaml
# → model.default: <id_du_modele_gratuit>
# → agent.reasoning_effort: max
# → display.show_reasoning: true
```

### 4. Intégrer au routeur

Dans `~/.hermes/tools/model_router.py` :
- Ajouter le profil dans `PROFILES`
- Ajouter des règles de routage avec mots-clés pertinents
- Placer les règles en PRIORITÉ MAX si c'est un modèle puissant

## Modèles gratuits découverts (juillet 2026)

| Modèle | Taille | Contexte | Idéal pour |
|--------|--------|----------|------------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | 550B | 1M | Puissance brute, audits |
| `nvidia/nemotron-3-super-120b-a12b:free` | 120B | 262K | Tâches équilibrées |
| `google/lyria-3-pro-preview:free` | ? | 1M | Analyse, création |
| `google/gemma-4-31b-it:free` | 31B | 262K | Rapide, fiable |
| `google/gemma-4-26b-a4b-it:free` | 26B | 262K | Exécution, recherche |

## Anti-patterns

- Ne pas utiliser un modèle gratuit trop petit pour du deep work → frustration
- Ne pas juger uniquement sur la taille — le fournisseur compte (NVIDIA > startup inconnue)
- Toujours tester le modèle sur une tâche simple avant de l'intégrer définitivement
