# Hermes3D Gateway Adapter — architecture adaptateur (2026-08)

Le Studio Hermes3D se connecte désormais via le **Hermes Gateway Adapter** (`server/hermes-gateway-adapter.js`, port 18789), PAS directement au JSON-RPC `hermes serve` (9120).

## Architecture

```
Browser <-> Studio Node (:3000) <-> Adapter WS (:18789, protocole Hermes3D gateway) <-> OpenRouter API
```

L'adapter traduit le protocole Hermes3D Gateway (connect.challenge, frames JSON) en appels OpenAI-compatible vers n'importe quelle API LLM.

## Variables d'env

| Variable | Défaut | Description |
|----------|--------|-------------|
| `HERMES_API_URL` | `http://localhost:8642` | URL de l'API OpenAI-compatible (OpenRouter, etc.) |
| `HERMES_API_KEY` | `""` | Bearer token pour l'API |
| `HERMES_ADAPTER_PORT` | `18789` | Port WebSocket du listener |
| `HERMES_MODEL` | `hermes` | Modèle par défaut (ex: `deepseek/deepseek-v4-flash:0731-cloud`) |
| `HERMES_AGENT_NAME` | `Hermes` | Nom affiché dans le bureau 3D |

## Lancement

```bash
cd /root/projets/hermes-3d
HERMES_API_URL=https://openrouter.ai/api/v1 \
HERMES_API_KEY=sk-or-... \
HERMES_ADAPTER_PORT=18789 \
HERMES_MODEL=deepseek/deepseek-v4-flash:0731-cloud \
node server/hermes-gateway-adapter.js
```

## Studio settings.json

Le fichier `~/.hermes/hermes3d/settings.json` doit pointer sur l'adapter :

```json
{
  "version": 1,
  "gateway": {
    "url": "ws://localhost:18789",
    "token": "",
    "adapterType": "hermes"
  },
  "activeFloorId": "hermes",
  "officeFloors": {
    "hermes": {
      "floorId": "hermes",
      "provider": "hermes",
      "gatewayUrl": "ws://localhost:18789",
      "status": "connecting"
    }
  }
}
```

Note : `token` peut être vide — l'adapter ne nécessite pas de token d'upstream pour la connexion de base.

## .env du projet

```
HERMES3D_GATEWAY_URL=ws://localhost:18789
NEXT_PUBLIC_GATEWAY_URL=ws://localhost:18789
HERMES3D_GATEWAY_TOKEN=1beb9c811b9b221a42b23a0ab04cb0e420a77708108921010873d2176ca35874
HERMES3D_GATEWAY_ADAPTER_TYPE=hermes-agent
UPSTREAM_ALLOWLIST=localhost,127.0.0.1
STUDIO_ACCESS_TOKEN=58c97a140210e9a85b8349a4eabc1892a0efe0c54c466d10
PORT=3000
HOST=0.0.0.0
```

## Agent CRUD via WebSocket API

L'adapter expose une API complète de gestion d'agents via messages JSON sur le WebSocket.

### Connexion

```python
# 1. Connect
ws.connect("ws://127.0.0.1:18789")
# → reçoit {"type":"event","event":"connect.challenge","payload":{"nonce":"..."}}

# 2. Répondre au challenge
ws.send({
  "type": "req", "method": "connect", "id": "c1",
  "params": {
    "auth": {"deviceToken": "hermes3d-admin"},
    "version": "1.0",
    "capabilities": ["chat", "agents", "cron", "files"]
  }
})
# → reçoit {"type":"res","id":"c1","ok":true,"payload":{"type":"hello-ok","protocol":3,...}}
```

### Créer un agent

```python
ws.send({
  "type": "req", "method": "agents.create", "id": "create_<name>",
  "params": {
    "name": "Le Scripte",
    "role": "Auteur Thriller",
    "systemPrompt": "Tu es l'assistant d'écriture...",
    "settings": {
      "model": "deepseek/deepseek-v4-flash:0731-cloud",
      "vibe": "Sombre, précis, immersif",
      "emoji": "✍️",
      "wipe": False,
      "continuity": True
    }
  }
})
```

### Lister les agents

```python
ws.send({
  "type": "req", "method": "agents.list", "id": "list_agents"
})
# → payload.agents[] avec id, name, role, systemPrompt, settings
```

### Modifier un agent

```python
ws.send({
  "type": "req", "method": "agents.update", "id": "update_<id>",
  "params": {
    "agentId": "le-scripte-62976c",
    "name": "Le Scripte",
    "soul": "# SOUL.md...",
    "role": "Auteur Thriller",
    "settings": {"vibe": "Sombre, précis, immersif", "emoji": "✍️"}
  }
})
```

### Capacités exposées par l'adapter

```
connect → hello-ok
agents.create, agents.list, agents.update, agents.delete
sessions.list, sessions.preview, sessions.patch, sessions.reset
chat.send, chat.abort, chat.history, agent.wait
status, config.get, config.set, config.patch
agents.files.get, agents.files.set
exec.approvals.get, exec.approvals.set, exec.approval.resolve
wake, skills.status, models.list, tasks.*
```

## Pièges

- **Ne PAS confondre architecture directe (hermes serve JSON-RPC) et adapter (port 18789)** : la directe parle JSON-RPC 2.0 sur `/api/ws?token=`, l'adapter parle Hermes3D Gateway Protocol sur `ws://...:18789`. Le Studio a été conçu pour l'adapter.
- **L'adapter nécessite une API LLM derrière** (OpenRouter, OpenAI, etc.) — sans `HERMES_API_KEY`, les appels agent échouent.
- **UPSTREAM_ALLOWLIST** obligatoire dans le `.env` du Node Studio, sinon le proxy gateway refuse les connexions montantes.
- **Le deviceToken** pour connecter l'adapter peut être n'importe quelle chaîne — `"hermes3d-admin"` suffit. Ce n'est PAS le STUDIO_ACCESS_TOKEN.
- **Ne pas lancer l'adapter sur le même port que `hermes serve`** — 9120 pour le backend JSON-RPC, 18789 pour l'adapter.
- **Adapter bindé sur 127.0.0.1 par défaut** — le `httpServer.listen(ADAPTER_PORT, "127.0.0.1", ...)` dans `hermes-gateway-adapter.js` écoute uniquement sur loopback. Le proxy Node (port 3000) devant l'adapter reçoit des connexions WebSocket du browser via le tunnel cloudflared (IP externe) **ou** depuis Windows (IP WSL). Dans les deux cas, la connexion upstream vers l'adapter vient d'une IP non-loopback → refusée silencieusement (le browser voit juste un timeout ou 1011). **Fix**: changer `"127.0.0.1"` en `"0.0.0.0"` dans `httpServer.listen()`. À faire après chaque `git pull` car le fichier est versionné et revient à `127.0.0.1` à chaque mise à jour.
- **Ne pas oublier `HOST=0.0.0.0`** pour le serveur Node Studio — sans ça, il écoute sur `127.0.0.1` et est inaccessible depuis Windows. Mettre dans le `.env` ou passer en variable d'env au démarrage.
- **Le `.env` n'est pas chargé par `node server/index.js`** — Next CLI (`npx next dev/start`) charge `.env` automatiquement, mais `node server/index.js` ne lit que `process.env`. Ajouter un chargeur dotenv manuel en haut de `server/index.js` (voir access-gate-302-fix.md ou la doc dotenv-loader.md).