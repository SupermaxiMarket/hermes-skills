---
name: claude-code-free-backends
description: "Use when setting up Claude Code with free backends."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Claude-Code, Ollama, GLM-5.2, Free, Proxy, Coding-Agent]
    related_skills: [claude-code]
---

# Claude Code — Backends Gratuits

Utiliser Claude Code **sans payer Anthropic** en passant par un proxy qui traduit les appels API Anthropic vers Olama, NVIDIA NIM, OpenAI ou Gemini.

## Architecture

```
Claude Code ──► Proxy :8082 ──► LiteLLM ──► Olama ──► Modèle (GLM 5.2, etc.)
(ANTHROPIC_BASE_URL)    (traduction)      (localhost:11434)
```

Le proxy utilisé : [claude-code-ollama-proxy](https://github.com/mattlqx/claude-code-ollama-proxy) — FastAPI + LiteLLM.

## Setup complet (Ollama + GLM 5.2 Cloud)

### 1. Prérequis

```bash
# Ollama (si pas déjà installé)
apt-get install -y zstd
curl -fsSL https://ollama.com/install.sh | sh

# Node + npm (pour installer Claude Code)
npm install -g @anthropic-ai/claude-code

# Proxy
git clone https://github.com/mattlqx/claude-code-ollama-proxy.git
cd claude-code-ollama-proxy
uv sync
```

### 2. Pull GLM 5.2 Cloud

```bash
ollama pull glm-5.2:cloud
ollama login  # ⚠️ OBSOLÈTE — modèles :cloud payants depuis août 2026
```

**GLM 5.2** : 744B params MoE (~40B actifs), 976K tokens contexte, licence MIT. Comparable à Claude Opus 4.8 sur les benchmarks de code. Le tag `:cloud` utilise l'inférence hébergée Z.ai — pas de GPU nécessaire.

### 3. Configurer le proxy

Ajouter `glm-5.2:cloud` dans `OLLAMA_MODELS` (server.py) :

```python
OLLAMA_MODELS = [
    # ... autres modèles ...
    "glm-5.2:cloud",
]
```

Créer `.env` :

```env
PREFERRED_PROVIDER="ollama"
OLLAMA_API_BASE="http://localhost:11434"
BIG_MODEL="glm-5.2:cloud"
SMALL_MODEL="glm-5.2:cloud"
ANTHROPIC_API_KEY=""
OPENAI_API_KEY=""
GEMINI_API_KEY=""
```

### 4. Lancer le proxy

```bash
cd claude-code-ollama-proxy
uv run uvicorn server:app --host 0.0.0.0 --port 8082 &
```

### 5. Lancer Claude Code

```bash
ANTHROPIC_BASE_URL=http://localhost:8082 claude
```

Pour usage fréquent, créer un alias dans `~/.bashrc` :

```bash
alias claude-free='ANTHROPIC_BASE_URL=http://localhost:8082 /root/.hermes/node/bin/claude'
```

## Backends alternatifs

| Backend | Modèle | Coût | Setup |
|---------|--------|------|-------|
| ~~Ollama Cloud~~ | `glm-5.2:cloud` | Payant (abonnement) depuis 08/2026 | Voir alternatives gratuites ci-dessous |
| **NVIDIA NIM** | `glm-5.2` | Gratuit (40 req/min) | Via Jan AI ou proxy custom |
| **Ollama local** | `codellama:34b`, `qwen3:32b` | Gratuit (GPU requis) | `OLLAMA_API_BASE` local |
| **Gemini** | `gemini-2.5-pro` | Gratuit (limité) | `PREFERRED_PROVIDER=google` + clé |
| **OpenAI** | `gpt-4.1` | Payant | `PREFERRED_PROVIDER=openai` + clé |

## Vérification

```bash
# Test Olama
ollama run glm-5.2:cloud -- "reply OK"

# Test proxy
curl -s http://localhost:8082/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: test" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"claude-sonnet-4-6","max_tokens":20,"messages":[{"role":"user","content":"Bonjour"}]}'

# Test Claude Code
ANTHROPIC_BASE_URL=http://localhost:8082 claude -p "Dis bonjour en français" --max-turns 1
```

## Dépannage

| Erreur | Cause | Solution |
|--------|-------|----------|
| `"Unauthorized"` | Pas de login Olama | `ollama login` |
| `claude: command not found` | PATH incomplet | Ajouter `$(npm config get prefix)/bin` au PATH |
| `Connection refused` Olama | Service pas démarré | `ollama serve` ou `systemctl start ollama` |
| Proxy `APIConnectionError` | Olama injoignable | Vérifier `curl http://localhost:11434/api/tags` |
| Lenteur GLM 5.2 Cloud | Quota Z.ai (3× peak 14h-18h UTC+8) | Utiliser en off-peak ou fallback GLM-4.7 |

## Notes Hermes/WSL

- npm prefix = `/root/.hermes/node/bin` (pas dans PATH par défaut)
- Olama sur Windows pas accessible depuis WSL → installer Olama dans WSL
- Proxy et Olama tournent localement, pas besoin de VPS externe