# Hermes3D Agent Management — création, protection, outils

## Créer des agents via l'adapter WebSocket API

L'adapter Hermes Gateway (`server/hermes-gateway-adapter.js`, port 18789) expose une API WebSocket pour gérer les agents.

### Connexion et création

```python
import asyncio, websockets, json

async def main():
    async with websockets.connect("ws://127.0.0.1:18789", open_timeout=5) as ws:
        # 1. Lire le challenge
        await ws.recv()  # {"type":"event","event":"connect.challenge","payload":{"nonce":"..."}}
        
        # 2. Connect
        await ws.send(json.dumps({
            "type": "req", "method": "connect", "id": "c1",
            "params": {"auth": {"deviceToken": "hermes3d-admin"}, "version": "1.0"}
        }))
        resp = json.loads(await ws.recv())
        # resp.ok == True → hello-ok
        
        # 3. Créer un agent
        await ws.send(json.dumps({
            "type": "req", "method": "agents.create", "id": "create_agent",
            "params": {
                "name": "Le Scripte",
                "role": "Auteur Thriller",
                "systemPrompt": "Tu es l'assistant d'écriture...",
                "settings": {
                    "model": "deepseek/deepseek-v4-flash-0731",
                    "vibe": "Sombre, précis, immersif",
                    "emoji": "✍️",
                    "wipe": False,
                    "continuity": True
                }
            }
        }))
        resp = json.loads(await ws.recv())
        # resp.ok == True, resp.payload.agentId == "le-scripte-<random6>"
```

### Protéger les agents contre l'orchestrateur

L'orchestrateur Hermes a des capacités tool-calling (spawn_agent, dismiss_agent, etc.). Quand on lui donne un objectif, il peut SUPPRIMER les agents permanents. Pour les protéger :

**1. Modifier le system prompt de l'orchestrateur** :

```python
await ws.send(json.dumps({
    "type": "req", "method": "agents.update", "id": "u1",
    "params": {
        "agentId": "hermes",
        "systemPrompt": """...YOUR PERMANENT TEAM (NEVER dismiss these):
- Le Scripte (Auteur Thriller)
- The Builder (Développeur Full-Stack)
- Oracle (Veille IA & Tendances)
- Content King (Stratège Contenu)
- Vigilance (Activiste)
- Link Builder (Stratège SEO)

These agents are permanent. You may spawn temporary agents for specific tasks,
but NEVER dismiss the permanent team members above..."""
    }
}))
```

**2. Lister les agents régulièrement** pour vérifier qu'ils sont toujours là :
```python
await ws.send(json.dumps({"type": "req", "method": "agents.list", "id": "l1"}))
agents = json.loads(await ws.recv()).get("payload", {}).get("agents", [])
```

### Assigner des bureaux (deskAssignments)

Les agents apparaissent dans le bureau 3D via `deskAssignments` dans `~/.hermes/hermes3d/settings.json`.

```json
{
  "deskAssignments": {
    "hermes": {
      "deskObjectId": "desk_a",
      "seatAnchor": { "x": 260, "y": 375 },
      "facingDegrees": 180
    },
    "le-scripte": {
      "deskObjectId": "desk_b",
      "seatAnchor": { "x": 480, "y": 375 },
      "facingDegrees": 180
    },
    "the-builder": {
      "deskObjectId": "desk_c",
      "seatAnchor": { "x": 700, "y": 375 },
      "facingDegrees": 180
    },
    "oracle": {
      "deskObjectId": "meeting_table",
      "seatAnchor": { "x": 1200, "y": 390 },
      "facingDegrees": 270
    },
    "content-king": {
      "deskObjectId": "meeting_table",
      "seatAnchor": { "x": 1240, "y": 350 },
      "facingDegrees": 0
    },
    "vigilance": {
      "deskObjectId": "meeting_table",
      "seatAnchor": { "x": 1280, "y": 390 },
      "facingDegrees": 90
    },
    "link-builder": {
      "deskObjectId": "meeting_table",
      "seatAnchor": { "x": 1240, "y": 430 },
      "facingDegrees": 180
    }
  }
}
```

Les bureaux disponibles dans l'office par défaut :
- `desk_a` (x:260, y:350) — bureau solo gauche
- `desk_b` (x:480, y:350) — bureau solo centre
- `desk_c` (x:700, y:350) — bureau solo droit
- `meeting_table` (x:1240, y:390) — table réunion (multi-place)

Le `seatAnchor` positionne l'avatar devant le bureau avec `facingDegrees` pour l'orientation.

### Ajouter des outils customs à l'adapter

**Important** : le fichier `server/hermes-gateway-adapter.js` est versionné. Les modifications seront perdues au prochain `git pull`.

#### 1. Ajouter la méthode dans `handleMethod()` (switch)

Trouver la section `handleMethod` (autour de la ligne 830) et le `default:` (autour de 1168). Ajouter AVANT `default:` :

```javascript
case "tools.web_search": {
      const query = typeof p.query === "string" ? p.query.trim() : "";
      if (!query) return resOk(id, { error: "Missing query" });
      return new Promise((resolve) => {
        const cp = require("child_process");
        const fs = require("fs");
        const scriptPath = "/tmp/hermes_web_search.py";
        const pyCode = [
          "import json, sys",
          "sys.path.insert(0, '" + require("os").homedir() + "/.hermes/tools')",
          "from hermes_tools import web_search",
          "result = web_search(query=" + JSON.stringify(query) + ", limit=5)",
          "print(json.dumps(result))"
        ].join("\n");
        fs.writeFileSync(scriptPath, pyCode);
        cp.exec("python3 " + scriptPath, { timeout: 15000 }, (err, stdout) => {
          if (err) return resolve(resOk(id, { error: String(err) }));
          try {
            const data = JSON.parse(stdout);
            resolve(resOk(id, data));
          } catch { resolve(resOk(id, { raw: stdout })); }
        });
      });
    }

    case "tools.news_brief": {
      const fs = require("fs");
      const mdPath = "/tmp/hermes-news-brief.md";
      const jsonPath = "/tmp/hermes-news-brief.json";
      const format = typeof p.format === "string" ? p.format : "md";
      if (format === "json" && fs.existsSync(jsonPath)) {
        const data = JSON.parse(fs.readFileSync(jsonPath, "utf8"));
        return resOk(id, data);
      }
      if (fs.existsSync(mdPath)) {
        const md = fs.readFileSync(mdPath, "utf8");
        return resOk(id, { format: "markdown", content: md });
      }
      return resOk(id, { error: "No news brief yet. Run the cron job first." });
    }
```

#### 2. Ajouter les méthodes dans la liste des features (hello-ok)

Trouver la ligne `features: { methods: [...]` (autour de 1264) et ajouter `"tools.web_search","tools.news_brief",` dans le tableau.

```javascript
features: { methods: ["agents.list","agents.create","agents.delete","agents.update",
  "sessions.list","sessions.preview","sessions.patch","sessions.reset",
  "chat.send","chat.abort","chat.history","agent.wait",
  "tools.web_search","tools.news_brief",  // <-- AJOUTER ICI
  "status","config.get","config.set","config.patch",
  ...
```

#### 3. Redémarrer l'adapter

```bash
pkill -f 'hermes-gateway-adapter' 2>/dev/null
sleep 2
node server/hermes-gateway-adapter.js
```

### Vérifier les agents et outils

```python
async with websockets.connect("ws://127.0.0.1:18789", open_timeout=5) as ws:
    await ws.recv()  # challenge
    await ws.send(json.dumps({"type":"req","method":"connect","id":"c1",
        "params":{"auth":{"deviceToken":"test"},"version":"1.0"}}))
    resp = json.loads(await ws.recv())
    methods = resp.get("payload",{}).get("features",{}).get("methods",[])
    print(f"tools.web_search présent: {'tools.web_search' in methods}")
    print(f"tools.news_brief présent: {'tools.news_brief' in methods}")
```