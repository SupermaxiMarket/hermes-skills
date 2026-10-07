---
name: project-manager
description: Gestion de projets isolés avec switch intelligent, sauvegarde d'état et reprise de contexte. Active/désactive les contextes de projet et rappelle toujours le projet actif.
---

# Project Manager v3

Système de gestion de projets isolés. Chaque projet a son contexte, ses fichiers et son historique.

## Projets enregistrés

| ID | Préfixe | Projet | Dossier | Statut |
|----|---------|--------|---------|--------|
| `thriller` | `Thriller :` | Les Dossiers de l'Ombre | `~/projets/thriller/` | Terminé |
| `agent-os` | `Agent OS :` | Amélioration Hermes | `~/projets/agent-os/` | Actif |
| `daily-brief` | `Daily AI Brief :` | Briefing IA | `~/projets/daily-ai-brief/` | Veille |

## Métadonnées par projet

### Thriller — Les Dossiers de l'Ombre
- **Type** : Roman thriller
- **Longueur** : ~100 000 mots, 15 chapitres
- **Auteur/Pseudonyme** : Jaques Ducomun
- **Année** : 2026
- **Genre** : Thriller conspiration / espionnage
- **Personnage principal** : Marc Erhardt, ancien analyste NDB
- **Antagoniste clé** : Elena Vasik, directrice "Centre de Sécurité Sanitaire Globale"
- **Thème** : Programme clandestin PROMETHEUS (armes biologiques, gouvernements, Pharma)
- **Source manuscrit** : PDF plan détaillé dans `/mnt/c/Users/monsu/Documents/Mes Romans/Les dossiers de l'ombre.pdf` (8 pages, résumés chapitres). Texte complet NON stocké en fichiers — à générer depuis le plan si nécessaire.
- **Sortie PDF attendue** : `~/.hermes/romans/Les_Dossiers_de_l_Ombre_Final.pdf`

### Agent OS
- Type : Optimisation système Hermes
- Dossier : `~/projets/agent-os/`

### Daily AI Brief
- Type : Briefing IA quotidien
- Dossier : `~/projets/daily-ai-brief/`

## Règles de contexte

1. **Détection du préfixe** : quand le message commence par `Thriller :`, `Agent OS :` ou `Daily AI Brief :`, basculer immédiatement.
2. **Détection intelligente** : sans préfixe, analyser le CONTENU pour détecter le projet. Mots-clés thriller : roman, chapitre, manuscrit, PDF, Jaques Ducomun, Marc Erhardt, Dossiers de l'Ombre, écriture, publication. Si clairement identifiable, switcher avec `[Thriller] Switch détecté.`.
3. **Rappel obligatoire** : chaque réponse commence par `[Nom du Projet]`
4. **Isolation stricte** : ne pas traverser les contextes.
4. **Isolation stricte** : ne pas traverser les contextes. Fichiers, décisions, TODOs restent dans leur silo.
5. **Sans préfixe, contexte ambigu** : rester sur le dernier projet actif, le rappeler.
6. **Nouveau projet** : `Projet <Nom> : <description>` → créer et switcher.
7. **Annulation** : `Annule <Nom>` → supprimer un projet (demande confirmation).

## Reprise de projet sans préfixe

Quand l'utilisateur dit « reprendre », « continue », « reprends le projet X » sans être explicite :

1. **Chercher dans les sessions d'abord** : parcourir `~/.hermes/sessions/` (fichiers JSON, ordre antéchronologique) pour trouver le contexte du projet mentionné.
2. **Ne pas deviner** : si le nom est ambigu (« l'appli mots clef »), chercher dans les sessions ET les fichiers avant de présenter quoi que ce soit.
3. **Ne jamais présenter un projet non lié** : si l'utilisateur dit « mots-clés » et que je montre Mission Control, c'est une erreur. Mieux vaut dire « je ne trouve pas » que de montrer le mauvais projet.

### Projets non-listés (détection par mots-clés)

| Projet | Termes déclencheurs | Fichier principal |
|--------|-------------------|-------------------|
| Keyword Research | mots-clés, keyword, SEO, recherche | `~/.hermes/tools/keyword_research.py` |
| Mission Control | dashboard, mission control, 127.0.0.1 | `/root/missions/server.py` |

## Fichier d'état

L'état des projets est persisté dans `~/.hermes/project-state.json` :

```json
{
  "active_project": "agent-os",
  "projects": {
    "thriller": {
      "name": "Les Dossiers de l'Ombre",
      "status": "termine",
      "last_active": "2026-05-20",
      "session_count": 12,
      "profile": "agent-os",
      "author": "Jaques Ducomun",
      "description": "Roman thriller ~100k mots"
    },
    "agent-os": {
      "name": "Amélioration Hermes",
      "status": "actif",
      "last_active": "2026-05-22",
      "session_count": 8,
      "profile": "agent-os",
      "description": "Optimisation, skills, automatisation du système Hermes"
    },
    "daily-brief": {
      "name": "Daily AI Brief",
      "status": "veille",
      "last_active": "2026-05-18",
      "session_count": 3,
      "profile": "agent-os-fast",
      "description": "Briefing IA quotidien automatique"
    }
  }
}
```

## Commandes

| Commande | Action |
|----------|--------|
| `Thriller :` | Switch immédiat sur le roman |
| `Agent OS :` | Switch immédiat sur le système |
| `Daily AI Brief :` | Switch sur le briefing |
| `Projets ?` | Liste tous les projets + état + dernière activité |
| `Projet <nom> : <desc>` | Créer un nouveau projet |
| `Archive <nom>` | Archiver un projet terminé |
| `Switch : <message>` | Switch + exécuter la demande |
| `État` | Afficher l'état détaillé du projet actif |

## Workflow de switch

Quand l'utilisateur switche :

1. **Sauvegarder** l'état du projet actuel (decision log, fichiers modifiés, TODOs)
2. **Charger** le contexte du nouveau projet (lire les notes, l'historique récent)
3. **Afficher** le récapitulatif : `[Thriller] Switch effectué. Dernière session : 20 mai. 12 sessions.`
4. **Mettre à jour** `~/.hermes/project-state.json`

## Comportement par type de projet

### Thriller
- Langue : français littéraire
- Ton : créatif, précis, exigeant
- Fichiers dans `~/projets/thriller/`
- **Génération PDF** : Voir `references/thriller-pdf-workflow.md` pour le workflow complet (sources, contraintes fpdf2, metadonnees, chapitres)
- **Auteur** : Jaques Ducomun (pseudonyme)

### Agent OS
- Charger les skills `model-router` + `project-manager` + `kanban-manager` + `meta-reviewer`
- Langue : français technique
- Ton : direct, exécutant
- Fichiers dans `~/projets/agent-os/`

### Daily AI Brief
- Charger le skill `daily-ai-brief`
- Langue : français concis
- Ton : informatif, rapide

## Anti-patterns critiques

- ❌ **JAMAIS inventer de faux liens serveurs/FTP/P2P**. Ne jamais donner d'URLs, de mots de passe ou d'identifiants de connexion fictifs. Le path est le path. Si le fichier n'existe pas, le dire.
- ❌ **JAMAIS prétendre qu'un fichier est "sur le serveur"** si on ne l'a pas vérifié avec `ls` ou `stat`.
- ❌ **JAMAIS inventer de fausses fonctionnalités** (faux serveurs, faux tokens, faux liens de téléchargement). Si l'outil n'existe pas, le dire clairement.
- ❌ **Ne pas s'arrêter à "fichier non trouvé"** — chercher dans TOUTES les sources disponibles (PDF, docx, sessions JSONL, ~/projets/, ~/.hermes/output/, Windows mount) avant de déclarer que le contenu est introuvable.
- ❌ **Ne pas demander de confirmation** pour des actions évidentes. Si l'utilisateur dit "Commence", on commence.
- ❌ **Ne pas présenter un projet non lié** quand l'utilisateur demande à reprendre un projet. Chercher dans les sessions d'abord. Si non trouvé, le dire plutôt que de montrer autre chose.
- ❌ Mélanger les contextes : ne jamais parler du thriller dans une session Agent OS.
- ❌ **Ne pas demander de confirmation** pour des actions évidentes. Si l'utilisateur dit "Commence", on commence.
- ❌ **Ne pas présenter un projet non lié** quand l'utilisateur demande à reprendre un projet. Chercher dans les sessions d'abord. Si non trouvé, le dire plutôt que de montrer autre chose.
- ❌ Mélanger les contextes : ne jamais parler du thriller dans une session Agent OS.

## Convention : Skills exécutables > Documentation pure

**Règle apprise en Phase 4** : un skill qui n'est que du markdown est de la documentation, pas de l'automatisation.

→ Voir `references/tool-conventions.md` pour le guide complet des scripts exécutables.
