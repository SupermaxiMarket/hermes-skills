# Recette détaillée : Claude Code + GLM 5.2 Cloud (session du 29/07/2026)

## Contexte

L'utilisateur voulait reproduire le setup d'une vidéo YouTube (obL4QzS4I-4) montrant Claude Code avec GLM 5.2 Cloud via Olama sur un VPS Hostinger. Adapté pour WSL local (pas de VPS).

## Chronologie de la session

1. **Installation Claude Code** : `npm install -g @anthropic-ai/claude-code` → installé dans `/root/.hermes/node/bin/` (prefix npm non-standard sur Hermes)
2. **PATH manquant** : le binaire `claude` pas trouvable → ajout de `/root/.hermes/node/bin` au PATH
3. **Installation Olama WSL** : nécessite `zstd` → `apt-get install -y zstd` puis `curl -fsSL https://ollama.com/install.sh | sh`
4. **Pull GLM 5.2 Cloud** : `ollama pull glm-5.2:cloud` — succès immédiat (le modèle Cloud ne pèse que 290B de manifest, l'inférence est chez Z.ai)
5. **Blocage "Unauthorized"** : les modèles Cloud exigent `ollama login` (compte gratuit)
6. **Proxy** : clone de `claude-code-ollama-proxy`, ajout de `glm-5.2:cloud` dans `OLLAMA_MODELS`, config `.env` avec `PREFERRED_PROVIDER=ollama`
7. **Lancement proxy** : `uv run uvicorn server:app --host 0.0.0.0 --port 8082 &` → répond mais renvoie "Unauthorized" d'Olama (login manquant)
8. **Alias bash** : `alias claude-free='ANTHROPIC_BASE_URL=http://localhost:8082 /root/.hermes/node/bin/claude'`

## État final

- ✅ Claude Code installé
- ✅ Olama + GLM 5.2 Cloud pullé
- ✅ Proxy configuré et lancé
- ⚠️ En attente de `ollama login` par l'utilisateur

## Fichiers modifiés

- `/root/.bashrc` : ajout PATH + alias
- `/root/claude-code-ollama-proxy/server.py` : ajout `glm-5.2:cloud` dans OLLAMA_MODELS
- `/root/claude-code-ollama-proxy/.env` : config Olama

## Leçons apprises

- **npm prefix Hermes** = `/root/.hermes/node/bin` — toujours vérifier avec `npm config get prefix`
- **Olama sur Windows inaccessible depuis WSL** — le firewall Windows bloque le port 11434. Installer Olama directement dans WSL.
- **Modèles Olama Cloud = pas de GPU** — le tag `:cloud` délègue l'inférence à Z.ai, pull quasi-instantané (290B de manifest)
- **`ollama login` obligatoire pour Cloud** — sans ça, "Unauthorized" sur tous les appels
- **Ne pas utiliser localhost.run** — déjà documenté dans la mémoire comme bloqué par antivirus