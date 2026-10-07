# Nemotron 550B — Quirks & Tricks

## include_reasoning: False obligatoire

Nemotron 550B (`nvidia/nemotron-3-ultra-550b-a55b:free`) a un comportement de "thinking" par défaut : il analyse d'abord la tâche en interne avant de répondre.

**Problème** : sans `include_reasoning: False` dans le payload API, le modèle :
- Passe d'abord en revue chaque point avant de répondre
- Consomme des tokens dans l'analyse, tronquant la réponse réelle
- Ignore les instructions "pas d'explication, juste le résultat"

**Solution** : ajouter `"include_reasoning": False` dans le payload OpenRouter :

```json
{
  "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
  "include_reasoning": false,
  "messages": [...]
}
```

Avec ce flag, le modèle répond directement, sans analyse préalable.

## Perfs observées

| Test | Tokens | Temps | Résultat |
|------|--------|-------|----------|
| Correction fautes (avec reasoning) | 468 | 5s | Analyse tronquée |
| Correction fautes (sans reasoning) | 264 | 8s | ✅ Parfait |
| Correction fautes (sans reasoning, v2) | 335 | 18s | Analyse tronquée (prompt pas assez strict) |
| Thriller 300 mots | 3397 | 19s | ✅ Excellent, coupé par max_tokens |
| Thriller complet | 3843 | 41s | ✅ Excellent |

## Bonnes pratiques

- Température 0.0-0.3 pour les tâches analytiques, 0.8 pour la création
- max_tokens: 1200 minimum pour du contenu créatif
- Prompt ultra-direct ("réponds UNIQUEMENT avec...") pour éviter les digressions
- Le modèle est gratuit via OpenRouter — pas de limite de coût