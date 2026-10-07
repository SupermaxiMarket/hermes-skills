---
name: kanban-manager
description: Système Kanban intelligent avec script CLI exécutable (~/.hermes/tools/kanban.py), priorisation automatique, deadlines, backups et persistance JSON multi-projets.
---

# Kanban Manager

**Script exécutable** : `~/.hermes/tools/kanban.py` (475 lignes, testé)
**Alias** : `kanban` → `python3 ~/.hermes/tools/kanban.py`
**Données** : `~/.hermes/kanban.json` (format multi-projets)
**Backups** : `~/.hermes/kanban_backups/` (rotation auto, 10 max)

## Utilisation rapide (CLI)

```bash
kanban list                          # Tableau complet
kanban list --projet thriller        # Par projet
kanban add "titre" -P high -d 2026-05-25 -t "tag1" -e "2h"
kanban move <id> in_progress|review|done
kanban delete <id>
kanban prioritize                    # Tri priorité + deadline
kanban detail <id>                   # Détail complet
kanban stats                         # Statistiques + retards
kanban archive --days 60             # Archive vieilles tâches
```

## Important : toujours utiliser le script

Ne **jamais** parser ou écrire `kanban.json` à la main. Utiliser `kanban.py`.
Le script gère les backups, la rotation, le format multi-projets et les validations.

## Structure du tableau

```
TO DO          IN PROGRESS       REVIEW            DONE
─────          ───────────       ──────            ────
[ ] Tâche     [>] En cours      [?] À valider     [✓] Terminé
[!!] Urgent   [>] En cours      [?] À valider     [✓] Terminé
[ ] Normal
```

## Fichier de données

Format multi-projets dans `~/.hermes/kanban.json` :

```json
{
  "projects": {
    "agent-os": { "columns": {...}, "settings": {...} },
    "thriller": { "columns": {...}, "settings": {...} }
  },
  "_updated": "2026-05-22T12:00:00+02:00"
}
```

Chaque projet a ses propres colonnes et settings, isolés. Le script `kanban.py --projet <nom>` gère la sélection automatiquement.

## Format d'une tâche

```json
{
  "id": "task-001",
  "title": "Optimiser le skill model-router",
  "description": "Ajouter fallback Qwen3 et tester",
  "priority": "high",
  "deadline": "2026-05-25",
  "tags": ["agent-os", "optimisation"],
  "created": "2026-05-22T09:00:00+02:00",
  "started": null,
  "completed": null,
  "estimation": "2h",
  "dependencies": []
}
```

## Commandes

| Commande | Action |
|----------|--------|
| `Kanban` | Afficher le tableau du projet actif |
| `Kanban <projet>` | Afficher le tableau d'un autre projet |
| `Kanban + <titre>` | Ajouter une tâche en TODO |
| `Kanban !! <titre>` | Ajouter une tâche URGENTE |
| `Kanban > <id>` | Déplacer en IN PROGRESS |
| `Kanban ? <id>` | Déplacer en REVIEW |
| `Kanban ✓ <id>` | Déplacer en DONE |
| `Kanban X <id>` | Supprimer une tâche |
| `Kanban @ <id>` | Voir le détail d'une tâche |
| `Kanban tri` | Réorganiser par priorité + deadline |

## Règles de priorisation automatique

Au `Kanban tri`, les tâches sont réordonnées selon :

1. **URGENT** (deadline < 24h) → tout en haut
2. **HIGH** (deadline < 72h) → après les urgences
3. **MEDIUM** → milieu
4. **LOW** → fin de colonne
5. Tâches sans deadline → après les LOW

## Règles métier

- Max 3 tâches en IN PROGRESS simultanément (bloque l'ajout)
- Une tâche en REVIEW depuis > 48h → rappel automatique
- Une tâche urgente créée → notifier
- Deadlines dépassées → marquer `[EN RETARD]`
- Tâches en DONE depuis > 30 jours → archiver automatiquement

## Intégration avec Project Manager

Au switch de projet (`Thriller :`, `Agent OS :`, etc.), le Kanban Manager charge automatiquement le kanban du projet cible.

Le résumé de switch inclut :
```
[Agent OS] Switch effectué.
Kanban : 3 TODO | 1 IN PROGRESS | 2 REVIEW | 12 DONE
Prochaine deadline : 25 mai (Optimiser model-router)
```

## Fichier de rappels

`~/projets/<projet>/reminders.json` :
```json
{
  "pending_reviews": ["task-003", "task-007"],
  "overdue": ["task-012"],
  "due_today": ["task-015"],
  "updated": "2026-05-22"
}
```

## Workflow typique

```
Toi →   Kanban
Moi →   [Agent OS] Tableau Kanban :
        ╔══════════════════════════════════════════╗
        ║ TO DO (3)                               ║
        ║ [!!] Corriger bug PDF emoji       [25/05]║
        ║ [HI] Optimiser model-router       [27/05]║
        ║ [LO] Nettoyer vieux skills         [—]  ║
        ╠══════════════════════════════════════════╣
        ║ IN PROGRESS (1)                         ║
        ║ [>] Kanban Manager               [22/05]║
        ╠══════════════════════════════════════════╣
        ║ REVIEW (0)                              ║
        ║ (vide)                                  ║
        ╠══════════════════════════════════════════╣
        ║ DONE (12)                               ║
        ║ [✓] Créer SOUL.md                [22/05]║
        ║ [✓] Créer USER.md                [22/05]║
        ║ ... (+10 autres)                        ║
        ╚══════════════════════════════════════════╝

Toi →   Kanban + Créer le cronjob pour le Meta Reviewer
Moi →   [Agent OS] Tâche ajoutée en TODO : "Créer le cronjob pour le Meta Reviewer" [MEDIUM]

Toi →   Kanban > task-015
Moi →   [Agent OS] "Créer le cronjob pour le Meta Reviewer" → IN PROGRESS
        ⚠️ 2/3 slots IN PROGRESS utilisés.
```