---
name: obsidian-moc-generator
description: "Génère une Map of Content (MOC) dynamique pour un vault Obsidian, listant les notes par catégorie avec statistiques et liens."
platforms: [linux, macos, windows]
---
# Obsidian MOC Generator Skill

Ce skill crée ou met à jour une note "Map of Content" (MOC) dans le dossier `00-Inbox` du vault Obsidian. Il fournit une vue d'ensemble du vault avec :

- Liste des notes par dossier (Projects, Areas, Resources, Archives, Journal, AgentOS)
- Statistiques : nombre total de notes, notes par catégorie, notes récentes
- Liens vers les notes orphelines (sans liens entrants/sortants détectés)
- Section pour ajouter des idées rapides

## Comment ça marche

Le skill parcourt récursivement le vault Obsidian (configurable) pour trouver tous les fichiers `.md`. Il génère ensuite une note MOC avec la structure suivante :

```
# 🗺️ Map of Content

## 📊 Statistiques
- **Total notes** : X
- **Notes aujourd'hui** : Y
- **Cette semaine** : Z

## 📁 Par catégorie
### Projects ([[01-Projects]])
- [[note1]]
- [[note2]]

### Areas ([[02-Areas]])
- ...

## 📅 Journal récent
- [[2026-05-26]]
- [[2026-05-25]]

## 🏷️ Tags populaires
- #project (5)
- #idea (3)

## 🔗 Notes orphelines (à lier)
- [[isolated-note]]

## ✏️ Idées rapides
- [ ] 
- [ ] 
```

## Utilisation

```bash
# Depuis le contexte Hermes :
hermes skill run obsidian-moc-generator
# Ou directement :
python3 ~/.hermes/skills/devops/obsidian-moc-generator/scripts/generate_moc.py
```

## Configuration

Le skill utilise les variables suivantes (modifiables dans le script) :
- `VAULT_PATH` : chemin vers le vault Obsidian (défaut : `~/obsidian-vault`)
- `MOC_PATH` : chemin de la note MOC (défaut : `VAULT_PATH / "00-Inbox" / "🗺️ Map of Content.md"`)
- `INCLUDE_FOLDERS` : liste des dossiers à inclure dans la MOC
- `EXCLUDE_FOLDERS` : dossiers à exclure (ex: `.obsidian`)

## Sécurité

- Le skill ne lit que des fichiers `.md` dans le vault configuré.
- Il ne modifie que la note MOC spécifiée (écrasement complet).
- Aucune connexion réseau n'est requise.

## Dépendances

- Python 3.6+ (standard dans l'environnement Hermes)
- Aucun package externe nécessaire (utilise uniquement la bibliothèque standard)