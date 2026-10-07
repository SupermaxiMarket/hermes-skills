# Conventions des outils exécutables Agent OS

## Emplacements standards

```
~/.hermes/tools/            → Scripts Python exécutables (CLI)
~/.hermes/kanban.json       → Données persistantes multi-projets
~/.hermes/kanban_backups/   → Backups horodatés automatiques
~/projets/<projet>/         → Fichiers spécifiques au projet
```

## Règles pour les scripts

1. **Pas de parsing JSON manuel par l'assistant** — toujours passer par un script
2. **Backup automatique** avant chaque écriture
3. **Format multi-projets** quand pertinent (`{"projects": {"nom": {...}}}`)
4. **Validation des entrées** — colonnes valides, priorités, IDs existants
5. **Messages clairs** — succès/erreur en français avec emojis discrets
6. **Pas de dépendances lourdes** — stdlib Python uniquement (sauf fpdf2 pour PDF)

## Pattern de script CLI

```python
#!/usr/bin/env python3
"""Description courte. Usage: outil.py <commande> [options]"""

import argparse
import json
from pathlib import Path

DATA_FILE = Path.home() / ".hermes" / "donnees.json"
BACKUP_DIR = Path.home() / ".hermes" / "donnees_backups"

def backup(): ...
def load(): ...
def save(): ...

def cmd_list(data): ...
def cmd_add(data, args): ...

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    # ... sous-commandes ...
    args = parser.parse_args()
    # ... dispatch ...

if __name__ == "__main__":
    main()
```

## Conventions de nommage

- Noms en snake_case : `kanban.py`, `meta_review.py`
- Commandes en anglais (cohérent avec CLI Unix) : `list`, `add`, `move`
- Messages utilisateur en français
- IDs de tâches : `task-{uuid8}` (ex: `task-a1b2c3d4`)

## Skills vs Scripts

| Skill (SKILL.md) | Script (.py) |
|------------------|--------------|
| Explique QUOI et POURQUOI | Exécute COMMENT |
| Doc de référence | Automatisation |
| Lu par l'assistant | Lancé par l'assistant ou l'utilisateur |
| Immutable (sauf patch) | Évolue avec les besoins |
