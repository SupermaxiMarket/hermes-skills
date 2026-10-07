# Agent News Brief — script-based cron pour données fraîches

## Problème

Les agents Hermes3D (Oracle, Content King, etc.) n'ont pas accès à l'actualité en temps réel. Le LLM derrière l'adapter (OpenRouter) a des connaissances figées à sa date d'entraînement. Impossible de poster du contenu d'actualité.

## Solution : cron + script news-fetcher

Un cron Hermes exécute un script Python toutes les 6h qui va chercher les news via `web_search` et les sauvegarde dans `/tmp/hermes-news-brief.json` et `/tmp/hermes-news-brief.md`. Les agents peuvent ensuite lire ce cache via `tools.news_brief`.

### 1. Script news-fetcher

Placer dans `~/.hermes/scripts/news-fetcher.py` :

```python
#!/usr/bin/env python3
import json, os, sys
sys.path.insert(0, os.path.expanduser("~/.hermes/tools"))
from hermes_tools import web_search
from datetime import datetime

def fetch_news():
    queries = [
        "IA intelligence artificielle actualités",
        "AI artificial intelligence news today",
        "LLM language model release news",
        "cybersécurité actualités",
        "tech transition écologique numérique",
    ]
    all_news = []
    for q in queries:
        results = web_search(query=q, limit=5)
        if results.get("success"):
            for item in results["data"]["web"]:
                all_news.append({
                    "title": item["title"],
                    "url": item["url"],
                    "snippet": item["description"],
                    "query": q
                })
    
    now = datetime.now().isoformat()
    with open("/tmp/hermes-news-brief.json", "w") as f:
        json.dump({"fetched_at": now, "count": len(all_news), "news": all_news}, f, indent=2)
    
    with open("/tmp/hermes-news-brief.md", "w") as f:
        f.write(f"# Daily AI Brief — {datetime.now().strftime('%d/%m/%Y')}\n\n")
        for i, item in enumerate(all_news, 1):
            f.write(f"### {i}. {item['title']}\n")
            f.write(f"{item['snippet'][:200]}...\n")
            f.write(f"🔗 {item['url']}\n\n")
    
    return {"count": len(all_news)}

if __name__ == "__main__":
    result = fetch_news()
    print(json.dumps(result))
```

### 2. Créer le cron (no-agent mode)

```bash
hermes cron create 'every 6h' \
  --name 'Agent News Brief' \
  --script news-fetcher.py \
  --no-agent \
  --deliver local
```

Le mode `--no-agent` exécute le script directement sans LLM, et son stdout est livré comme résultat.

### 3. Exécution immédiate

```bash
hermes cron run <job-id>
```

### 4. Vérification

```bash
cat /tmp/hermes-news-brief.md | head -20
```

### 5. Outil adapter pour les agents

Voir `hermes3d-agent-management.md` — ajouter `tools.news_brief` dans l'adapter pour que les agents puissent lire le cache.

### Pièges

- Le script doit être dans `~/.hermes/scripts/` (pas `~/.hermes/tools/`) — `hermes cron create --script` prend un nom relatif à ce dossier.
- `hermes_tools` (web_search, web_extract) sont disponibles dans `~/.hermes/tools/` — ajouter au `sys.path`.
- Les news sont en cache — pas en temps réel. Actualisation toutes les 6h.
- Le cron tourne dans le contexte Hermes (même venv, mêmes outils).