---
name: web-to-obsidian
description: "Écoute les messages Telegram (signets ou tweets) et les enregistre en markdown dans le vault Obsidian sous 04-Archives/WebClips/ avec balises appropriées."
platforms: [linux, macos, windows]
---
# Web‑to‑Obsidian Skill

Ce skill permet de capturer du contenu provenant de Telegram (un signet sous forme d’URL ou le texte d’un tweet) et de l’enregistrer automatiquement dans votre vault Obsidian, sous le dossier `04-Archives/WebClips/`. Chaque enregistrement est accompagné de balises (tags) Obsidian afin de faciliter la recherche et le lien avec vos autres notes.

## Fonctionnement

1. **Écoute Telegram** : le script utilise l’API `getUpdates` du Bot Telegram pour récupérer les nouveaux messages envoyés à votre bot ou dans le groupe configuré.
2. **Détection du type de contenu** :
   - Si le message contient une URL, le skill tente d’extraire le contenu de la page via `web_extract` (Hermes) et le convertit en markdown.
   - Si le message est du texte pur (par ex. un tweet copié‑collé), il est traité comme du markdown brut.
3. **Enregistrement dans Obsidian** : le contenu markdown est écrit dans un fichier nommé avec un horodatage sous `04-Archives/WebClips/`. Des balises Obsidian sont ajoutées en tête du fichier :
   - `#webclip` – indique que la note provient de ce skill.
   - `#source:telegram` – indique la provenance.
   - Si le contenu provient d’une URL, une balise `#source:url` est ajoutée ; sinon `#source:tweet`.
   - Le domaine de l’URL (sans `www.`) est ajouté comme balise lorsqu’il s’agit d’un signet (ex. `#example-com`).

## Prérequis

- Hermes Agent installé et fonctionnel (`hermes --version`).
- Un Bot Telegram créé (via @BotFather) avec son token accessible via la variable d’environnement `TELEGRAM_BOT_TOKEN`.
- L’ID du chat (ou du groupe) où le bot pourra recevoir les messages, accessible via `TELEGRAM_CHAT_ID`. Vous pouvez obtenir cet ID en envoyant un message au bot puis en appelant `https://api.telegram.org/bot<token>/getUpdates`.
- Accès en lecture/écriture au vault Obsidian créé par le skill `agent-os-integrator` (par défaut `/root/obsidian-vault`). Vous pouvez surcharger ce chemin avec la variable d’environnement `OBSIDIAN_VAULT_PATH`.
- Python 3.8+ (l’environnement virtuel Hermes est déjà actif).

## Installation du skill

Le skill est déjà installé via cette définition. Vous pouvez le lancer directement :

```bash
hermes skill run web-to-obsidian
```

Ou, pour exécuter le script seul :

```bash
python3 ~/.hermes/skills/note-taking/web-to-obsidian/scripts/run.py
```

## Utilisation

1. Assurez‑vous que les variables d’environnement sont définies (ex. dans votre `~/.bashrc` ou le fichier d’environnement Hermes) :
   ```bash
   export TELEGRAM_BOT_TOKEN="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
   export TELEGRAM_CHAT_ID="987654321"
   export OBSIDIAN_VAULT_PATH="/root/obsidian-vault"   # optionnel
   ```
2. Lancez le skill en tâche de fond ou via un planificateur (cron, systemd timer). Exemple de lancement simple :
   ```bash
   # Dans un tmux/screen ou en arrière‑plan :
   hermes skill run web-to-obsidian &
   ```
3. Dans Telegram, envoyez à votre bot :
   - Une URL (ex. `https://example.com/article`) → le skill téléchargera la page, en extraira le texte principal et l’enregistrera en markdown.
   - Du texte brut (ex. le contenu d’un tweet copié depuis Twitter) → il sera enregistré tel quel.
4. Dans Obsidian, ouvrez le vault et naviguez vers `04-Archives/WebClips/` pour voir les nouvelles notes. Elles seront préfixées d’un horodatage, par exemple `2026-06-06_05-30-12_webclip.md`.

## Personnalisation

- **Chemin du vault** : modifier la variable `VAULT_PATH` dans le script ou définir `OBSIDIAN_VAULT_PATH`.
- **Balises supplémentaires** : éditez la fonction `build_frontmatter` dans le script pour ajouter vos propres tags.
- **Format du nom de fichier** : changez la constante `FILENAME_FORMAT` dans le script.
- **Fréquence de polling** : la constante `POLL_INTERVAL_SECONDS` (par défaut 5 s) peut être ajustée.

## Sécurité

- Le skill ne fait que lire les messages Telegram et écrire dans votre vault local. Aucune donnée n’est envoyée à des tiers externes, sauf la requête `getUpdates` vers l’API Telegram et, en cas d’URL, la requête HTTP vers la page cible.
- Assurez‑vous que votre token de bot n’est pas partagé publiquement.
- Le skill ne supprime ni ne modifie de notes existantes ; il crée uniquement de nouveaux fichiers.

## Exemple de note générée

```markdown
---
tags:
  - webclip
  - source:telegram
  - source:url
  - example-com
---

# Titre de la page (extrait balise <h1> ou og:title)

Contenu extrait de la page web, formaté en markdown par Hermes `web_extract`.
Lien source : https://example.com/article
```

## Dépannage

- **Pas de nouveaux messages reçus** : vérifiez que `TELEGRAM_BOT_TOKEN` et `TELEGRAM_CHAT_ID` sont corrects et que le bot a bien reçu au moins un message (pour obtenir le `update_id` de départ).
- **Échec d’extraction d’URL** : le skill journalise l’erreur dans la console ; vous pouvez exécuter manuellement `hermes web_extract --urls <url>` pour tester.
- **Permissions d’écriture dans le vault** : assurez‑vous que l’utilisateur qui exécute le skill possède les droits d’écriture sur le répertoire du vault.

--- 

*Ce skill s’intègre parfaitement à l’Agent OS basé sur Hermes et Obsidian, permettant une capture fluide du contexte provenant de Telegram directement dans votre base de connaissances personnelle.*