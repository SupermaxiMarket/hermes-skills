# DO NOT EDIT — voir ci-dessous.

SKILL.md non modifiable depuis ce sous-agent à cause d'une collision de noms (deux skills `daily_ai_brief`). Le patch suivant est à appliquer :

## Patch manuel requis

Dans `productivity/daily_ai_brief/SKILL.md`, remplacer :

```
#### Format Synthèse Éditoriale (rapport Markdown enrichi)

Utilisé quand l'utilisateur demande une « synthèse éditoriale », un « rapport quotidien » détaillé, ou utilise le mot-clé « Pour Pierre ».
```

Par :

```
#### Format Synthèse Éditoriale (rapport Markdown enrichi)

Utilisé quand l'utilisateur demande une « synthèse éditoriale », un « rapport quotidien » détaillé, ou utilise le mot-clé « Pour Pierre ».

**Variante « Intelligence Empire Daily »** : quand l'utilisateur demande explicitement un rapport « Intelligence Empire Daily » ou fournit un brief structuré avec 5 sujets numérotés + sources. Ce format ajoute :
- Une **Ouverture Météo IA** en italique résumant tous les sujets
- Une section **📊 Tendances de fond** (tableau méga-tendances)
- Une section **🔮 Preview** (anticipation du lendemain)
- Des 📝 **Détails** factuels (pas juste une source)
- Signature spécifique « Rédigé par la rédaction d'Intelligence Empire »
- Contrainte renforcée : MAX **700 mots** de prose (vs 750 pour le standard)
- Voir `references/empire-format-2026-08-18.md` pour la structure complète et `/root/intelligence_empire_daily_2026-08-18.md` pour un exemple livré.
```

Puis dans `daily-ai-brief/SKILL.md` (v1, obsolète), ajouter un commentaire en haut :

```
> **OBSOLÈTE** — Utiliser `productivity/daily_ai_brief` (v2) à la place.
> Cette copie existe encore par collision de nom. À supprimer ou fusionner.
```