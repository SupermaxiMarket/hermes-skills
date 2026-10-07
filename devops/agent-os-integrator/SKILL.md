---
name: agent-os-integrator
description: "Installe et configure un Agent Operating System complet basé sur Hermes, Obsidian et les skills existants."
platforms: [linux, macos, windows]
---
# Agent OS Integrator Skill

Ce skill automatise la mise en place d'un Agent Operating System (AOS) conforme au blueprint décrit dans la vidéo YouTube fournie. Il regroupe :

1. **Foundation** : utilise l'environnement WSL/Linux existant.
2. **Memory** : crée et structure un vault Obsidian pour le contexte Infini.
3. **Brain** : s'appuie sur la configuration modèle actuelle d'Herme (OpenRouter/deepseek).
4. **Agents** : active les skills Hermes existants comme agents spécialisés (YouTube, GitHub, MCP, etc.).
## Command Center : lance le dashboard Hermes (TUI) et configure l'interface web optionnelle (port 9119 par défaut, configurable).
6. **Production Services** : configure les Kanban, objectifs, génération de contenu via les skills project-manager, kanban-manager, daily-ai-brief.
7. **Loop/Feedback** : installe des hooks qui sauvegardent les outputs dans le vault Obsidian pour enrichir le contexte.

## Prérequis

- Hermes Agent installé et fonctionnel (`hermes --version`).
- Git disponible.
- Python 3.8+ (venv Hermes déjà actif).
- Accès internet pour installer les dépendances Obsidian si nécessaire.

## Étapes d'exécution

Le skill fournit un script d'initialisation situé à `~/.hermes/skills/agent-os-integrator/scripts/init.py`. L'exécuter réalise :

1. Création du vault Obsidian sous `~/obsidian-vault` (ou chemin configurable).
2. Création de la structure de dossiers recommandée :
   - `00-Inbox`
   - `01-Projects`
   - `02-Areas`
   - `03-Resources`
   - `04-Archives`
   - `AgentOS/Context` (notes utilisateur, préférences, historique)
   - `AgentOS/Logs` (journal des interactions agents)
   - `AgentOS/Production` (résultats des skills de production)
3. Initialisation d'un fichier `AgentOS/Context/SOUL.md` avec votre profil utilisateur (copié depuis `~/.hermes/SOUL.md` si existant).
4. Lancement du gateway Hermes en arrière-plan (`hermes gateway start`).
5. Lancement du dashboard Hermes web en arrière-plan (`hermes dashboard --host 0.0.0.0 --port 9119 --no-open`).
6. Enregistrement d'un webhook de sortie : chaque fois qu'un skill produit un fichier ou du texte, une copie est placée dans `AgentOS/Logs/<timestamp>-<skill>.md`.
7. Affichage du tableau de bord des procédures suivantes :
   - Ouvrir Obsidian avec le vault créé.
   - Accéder au TUI Hermes via `hermes tui`.
   - Utiliser les skills de production (ex: `hermes run daily-ai-brief`).
   - Ouvrir le dashboard web à http://localhost:9119 (ou l'hôte/port configuré).

## Utilisation

```bash
# Depuis n'importe quel répertoire dans le contexte Hermes :
hermes skill run agent-os-integrator
# Ou directement :
python3 ~/.hermes/skills/agent-os-integrator/scripts/init.py
```

## Personnalisation

- Chemin du vault : modifier la variable `VAULT_PATH` dans le script.
- Modèle actif : ajuster via `hermes config set model.default <votre-modèle>` avant de lancer le skill.
- Agents supplémentaires : ajouter d'autres skills dans la liste `ACTIVE_AGENTS` du script.

## Précautions de sécurité

- Le skill ne modifie que des répertoires utilisateur (`~/obsidian-vault`, `~/.hermes`).
- Il ne supprime aucun fichier existant ; il crée uniquement ou ajoute des entrées.
- Le lancement du gateway Hermes se fait en arrière-plan avec sortie redirigée vers un log (`~/hermes-gateway.log`) pour éviter de bloquer le terminal.
- Aucune installation de paquets système nécessitant des privilèges root n'est requise.

## Vérification

Après exécution :
- Le dossier `~/obsidian-vault` doit contenir la structure décrite.
- Le processus `hermes gateway` doit être visible (`ps aux | grep hermes`).
- Le processus `hermes dashboard` doit être visible (`ps aux | grep hermes`).
- Un fichier de log `~/hermes-gateway.log` doit contenir les messages de démarrage.
- Un fichier de log `~/hermes-dashboard.log` doit contenir les messages de démarrage du dashboard.
- Un premier note `AgentOS/Context/bootstrapped.md` doit être présent indiquant la date et la version du skill.

## Désinstallation / Nettoyage

Pour retirer le vault Obsidian créé : `rm -rf ~/obsidian-vault`.
Pour arrêter le gateway : `pkill -f "hermes gateway"` ou consulter le log pour le PID.

Ce skill respecte la philosophie d'autonomie : aucune confirmation interactive n'est requise lors de l'exécution standard, tout en signalant clairement les actions effectuées.

## Dépannage

- **Installation de skills lente ou timeout** : Si la commande `hermes skills install <skill>` dépasse le délai d'attente, vérifiez votre connexion internet et essayez d'ajouter le drapeau `--yes` pour sauter les invites de confirmation. Vous pouvez également installer le skill directement depuis un fichier local ou un URL GitHub en spécifiant le chemin complet vers le SKILL.md.

- **Vérifier le registre** : Utilisez `hermes skills update` pour rafraîchir le cache du registre avant d'essayer à nouveau l'installation.

- **Compétences locales** : Si vous avez déjà le skill sous `~/.hermes/skills/`, vous pouvez le (ré)activer avec `hermes -s <skill>` ou `/skill <skill>` dans une session.