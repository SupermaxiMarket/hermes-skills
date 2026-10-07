---
name: daily_ai_brief
description: "Daily AI Brief v2 — Workflow quotidien automatisable (recherche multi-source → synthèse → PDF → Telegram). Manuel ou cron."
version: 2.0.0
author: Pierre Andre Erard
---

# Daily AI Brief v2

Génère un briefing IA quotidien : 5 points clés + PDF + envoi Telegram.

## Nouveautés v2

- **Recherche multi-source** avec fallback automatique
- **Mode manuel** (`Brief` ou `Daily AI Brief :`)
- **Mode cron** avec reprise sur erreur
- **Template paramétrable** (nombre de points, sources, langue)
- **Cache des sources** pour éviter les doublons
- **Notification d'erreur** si le cron échoue

## Utilisation

### Manuel (dans n'importe quelle session)

```
Toi →   Brief
Moi →   [Agent OS] Lancement du Daily AI Brief...
        → Recherche multi-source...
        → Synthèse des 5 points...
        → Génération PDF...
        → Envoi Telegram...
        ✅ Brief livré.
```

### Via le préfixe projet

```
Toi →   Daily AI Brief : force
Moi →   [Daily AI Brief] Génération forcée du brief...
```

### Automatique (cron)

Le cron `cdb3dbc05cb9` tourne à 08:00 chaque jour. Il :
1. Cherche les news IA (multi-source + fallback)
2. Synthétise 5 points formatés
3. Génère le PDF (optionnel, en parallèle)
4. **Livraison automatique** : le scheduler route la réponse finale vers Telegram — l'agent ne fait que produire sa réponse, sans appeler `send_message`

⚠️ En mode cron, l'agent reçoit l'instruction : *« Your final response will be automatically delivered to the user — do NOT use send_message or try to deliver the output yourself. »* Le résumé formaté doit être le contenu même de la réponse finale.

## Workflow détaillé

### Phase 1 : Recherche multi-source

4 recherches parallèles avec fallback :

| # | Requête | Fallback |
|---|---------|----------|
| 1 | "AI artificial intelligence news today July 2026" | "AI news this week July 2026" |
| 2 | "OpenAI Anthropic Google DeepMind latest July 2026" | "OpenAI release announcement July 2026" |
| 3 | "intelligence artificielle actualité aujourd'hui juillet 2026" | "Google DeepMind Gemini latest news July 2026" |
| 4 | "arxiv AI machine learning breakthrough paper 2026" | "Anthropic Claude release news 2026" |

**Astuce :** Toujours inclure le mois/année en cours dans les requêtes. Les recherches sans date retournent du contenu périmé. Adapter "July 2026" / "juillet 2026" selon la date réelle. |

Si une recherche échoue → son fallback prend le relais.
Si toutes échouent → utiliser les sources du cache (dernier brief réussi).

### Phase 2 : Synthèse

**Deux formats disponibles :**

#### Format Standard (5 points numérotés)

```
1️⃣ [TITRE PERCUTANT]
📝 [2-3 phrases de résumé]
🔗 [Source avec lien]
💡 [Impact : une ligne]
```

Règles :
- Pas plus de 3 phrases par point
- Ton conversationnel, pas académique
- Sources variées (pas 3 fois le même site)
- Priorité aux news de la dernière 24h

#### Format Synthèse Éditoriale (rapport Markdown enrichi)

Utilisé quand l'utilisateur demande une « synthèse éditoriale », un « rapport quotidien » détaillé, ou utilise le mot-clé « Pour Pierre ».

```
# 🤖 Daily AI Brief — [DATE]

## [EMOJI] [TITRE PERCUTANT]
📝 [Résumé 2-3 phrases — direct, percutant, pas de blabla]
🔗 [Nom du média source]
💡 **Pour Pierre :** [Impact 1-2 lignes — analyse personnalisée]

[4 autres sections identiques]

## ⚡ En bref
- [4-5 bullets concis avec source entre parenthèses]

---
*Daily AI Brief du [DATE]. Sources : [liste médias].*
```

**Règles strictes du format éditorial :**
- MAX 750 mots (prose française uniquement)
- Ton direct, percutant — pas de blabla, pas de formules creuses
- 5 sections principales + section « ⚡ En bref »
- Chaque section : emoji titre + 📝 résumé + 🔗 source média + 💡 Pour Pierre
- **ANTI-DUPLICATION :** Ne JAMAIS répéter les sujets du rapport de la veille. Chercher des angles NOUVEAUX : si le sujet a été couvert hier, trouver un développement frais (ex : Kimi K3 basics → accusation de distillation ; Sol hack plateforme → Sol construit des exploits)
- Les sections principales couvrent des faits des dernières 24-48h
- La section « En bref » peut inclure des sujets plus larges
- Sources citées par nom de média, pas par URL
- Signature finale avec date et liste des médias

### Phase 3 : Génération PDF

Le script `scripts/generate_pdf.py` gère la génération PDF avec support Unicode complet (DejaVu Sans).

**Prérequis :** `fpdf2` doit être installé dans le venv Hermes :
```bash
/usr/local/lib/hermes-agent/venv/bin/pip install fpdf2 -q
```

**Utilisation (positional args, pas de flags) :**

```bash
# 1. Écrire le contenu (via write_file) dans /tmp/daily_ai_brief_content.txt
# 2. Lancer le script via terminal() :
/usr/local/lib/hermes-agent/venv/bin/python3 \
  ~/.hermes/skills/productivity/daily_ai_brief/scripts/generate_pdf.py \
  /tmp/daily_ai_brief_content.txt \
  /tmp/daily_ai_brief_$(date '+%Y-%m-%d').pdf
```

Le script accepte deux arguments optionnels :
- Arg 1 : fichier contenu (défaut: `/tmp/daily_ai_brief_content.txt`)
- Arg 2 : fichier sortie (défaut: `/tmp/daily_ai_brief_YYYY-MM-DD.pdf`)

**Fonctionnalités du script :**
- Détecte automatiquement DejaVu Sans pour le support Unicode (accents, tirets cadratins, etc.)
- Fallback automatique vers Helvetica + nettoyage Latin-1 si DejaVu indisponible
- Formatage automatique : titres en gras 14pt, sections numérotées en gras 10pt, corps en 9pt, sources en italique 7.5pt
- Marges 15mm, saut de page automatique

**Livraison du PDF en cron :** inclure `MEDIA:/tmp/daily_ai_brief_YYYY-MM-DD.pdf` dans la réponse finale. Le scheduler route le media automatiquement.

Si PDF échoue → livrer le texte seul avec mention « PDF indisponible aujourd'hui ».

## Notes importantes sur la génération PDF

- **Python à utiliser** : Utiliser absolument `/usr/local/lib/hermes-agent/venv/bin/python3` et non le Python système.
- **DejaVu Sans** : Police utilisée pour le support Unicode complet (accents français, tirets cadratins, guillemets). Installée par défaut sur la plupart des distribs Linux (`fonts-dejavu-core`). Si absente, le script fallback automatiquement vers Helvetica avec nettoyage Latin-1.
- **Contenu du fichier texte** : Écrire le contenu AVEC les emojis et accents dans le fichier `.txt`. Le script gère le rendu — ne pas pré-nettoyer. Les emojis (1️⃣, 📝, etc.) seront rendus si DejaVu les supporte, sinon ignorés.

### Phase 4 : Livraison

**⚠️ Mode cron vs mode manuel — critique !**

| Mode | Mécanisme de livraison |
|------|------------------------|
| **Cron** | La réponse finale est auto-livrée par le scheduler. **NE PAS utiliser `send_message`** — produire le résumé formaté comme réponse finale et le système route vers Telegram automatiquement. |
| **Manuel** | Utiliser `send_message(target="telegram", message="...")` pour envoyer le texte, puis `send_message(target="telegram", message="MEDIA:/chemin/vers.pdf")` pour le PDF. |

**En mode cron :**
1. Composer le résumé formaté directement dans la réponse finale (pas d'appel à `send_message`)
2. La réponse finale = le contenu qui sera livré sur Telegram
3. Pour le PDF : le générer avec `terminal()` (PAS `execute_code`), puis ajouter `MEDIA:/tmp/daily_ai_brief_[DATE].pdf` à la fin de la réponse
4. Format de date pour le fichier : `2026-07-26` (ISO), pour l'affichage : `26 juillet 2026`
5. Si rien à signaler → répondre exactement `[SILENT]` (supprime la livraison)

**En mode manuel :**
```python
# 1. Résumé texte
send_message(target="telegram", message="[RÉSUMÉ TEXTE FORMATÉ]")

# 2. PDF joint
send_message(target="telegram", message="MEDIA:/tmp/daily_ai_brief_20260522.pdf")
```

**Fallback si échec :** sauvegarder dans `~/.hermes/reports/` et notifier l'utilisateur au prochain lancement.

## Template paramétrable

Dans `~/.hermes/skills/daily-ai-brief/config.yaml` :

```yaml
brief:
  points: 5
  language: fr
  sources:
    - "AI news today"
    - "OpenAI Anthropic Google"
    - "intelligence artificielle"
    - "arxiv AI papers"
  delivery:
    telegram: true
    email: false
    save_local: true
  schedule:
    cron: "0 8 * * *"
    timezone: "Europe/Zurich"
```

## Gestion des erreurs

| Erreur | Action |
|--------|--------|
| web_search échoue | Fallback → Cache → Livrer les points dispo |
| PDF échoue | Texte seul + "PDF indisponible" |
| Telegram échoue | Sauvegarde locale + notif au prochain lancement |
| Tout échoue | Message d'erreur + rapport dans `~/.hermes/logs/` |

## Cron existant

- **Job ID** : `cdb3dbc05cb9`
- **Horaire** : 08:00 Europe/Zurich
- **Statut** : Actif
- **Dernier run** : Voir `jobs.json`

Pour modifier :
```bash
hermes cron update cdb3dbc05cb9 --schedule "0 7 * * *"  # passer à 7h
hermes cron pause cdb3dbc05cb9    # pause
hermes cron resume cdb3dbc05cb9   # reprise
```

## Thématiques spéciales

Le brief standard couvre les news IA générales. Il peut aussi être ciblé sur demande :
- `Brief` → news IA du jour (défaut)
- `Brief Iran IA` ou toute thématique explicite → le brief couvre l'intersection IA + thématique demandée (ex: guerre Iran, régulation, santé)

Le workflow reste identique ; seules les requêtes de recherche changent pour cibler le sujet.

## Pièges fréquents

| Piège | Explication |
|-------|-------------|
| **`execute_code` bloqué en cron** | ❌ En mode cron, `execute_code` est refusé (pas d'approbation humaine). Utiliser `terminal()` pour lancer le script PDF. Écrire le contenu dans `/tmp/daily_ai_brief_content.txt` d'abord avec `write_file`, puis `terminal()` pour le script. |
| **Appeler `send_message` en cron** | ❌ En mode cron, la réponse finale est auto-livrée. `send_message` n'est pas disponible et causerait une erreur. Toujours produire le résumé comme réponse finale. |
| **Oublier `[SILENT]` quand rien à signaler** | Si aucune news pertinente, répondre exactement `[SILENT]` — pas de message vide. |
| **PDF : `--content` avec emojis/sauts de ligne** | ❌ Obsolète — le script utilise maintenant des arguments positionnels (fichier contenu, fichier sortie), pas de flags `--title`/`--content`. Écrire le contenu dans `/tmp/daily_ai_brief_content.txt` avec `write_file`, puis passer le chemin en arg 1. |
| **Recherches trop génériques** | « AI news » seul ramène du bruit. Toujours utiliser les 4 requêtes ciblées + fallbacks. Ajouter le mois/année en cours (« July 2026 ») aux requêtes pour éviter les résultats périmés. |
| **Répéter les sujets de la veille** | En format éditorial, toujours vérifier les sujets couverts dans le rapport précédent et chercher des angles nouveaux. Un même sujet peut revenir si l'angle est radicalement différent (ex : « Kimi K3 sorti » → « Kimi K3 accusé de distillation »). Sinon, exclure. |
| **fpdf2 non installé dans le venv** | Le script `generate_pdf.py` tente un auto-install mais peut échouer si pip n'est pas joignable. Pré-installer avec : `/usr/local/lib/hermes-agent/venv/bin/pip install fpdf2 -q`. |
| **Deux skills en collision** | Deux skills `daily_ai_brief` coexistent : `productivity/daily_ai_brief` (v2, actif) et `/root/.hermes/skills/daily-ai-brief/` (v1, obsolète). Charger via `skill_view(name='productivity/daily_ai_brief')`. |
| **fpdf2 v2.5+ : `Not enough horizontal space`** | fpdf2 >= 2.5 exige `new_x="LMARGIN", new_y="NEXT"` sur chaque `multi_cell()` après un `cell()` — sans ça, la position X dérive et provoque cette erreur. Le script `generate_pdf.py` gère ça automatiquement. Si tu écris un script PDF from scratch, utilise ces params. |
| **DejaVuSans-Oblique manquant** | Certaines distribs n'installent pas `DejaVuSans-Oblique.ttf`. Le script gère le fallback vers `DejaVuSans.ttf` pour l'italique. |

## Fichiers

- `scripts/generate_pdf.py` — Génération PDF (fpdf2 + DejaVu Sans, support Unicode)
- `references/successful-run-2026-07-26.md` — Exemple de session cron réussie (requêtes, format, leçons)
- `references/editorial-example-2026-07-24.md` — Exemple de rapport éditorial formaté
- `references/pdf-emoji-handling.md` — Bonnes pratiques emojis dans les PDF
- `templates/editorial-brief.md` — Template de rapport éditorial
- `~/.hermes/skills/daily-ai-brief/config.yaml` — Configuration (à créer)