---
name: content-strategy-automation
description: "Build 24/7 content analysis + idea agents with Hermes."
---

# Content Strategy Automation (Hermes Muse Pattern)

Build a 24/7 autonomous agent that analyzes content performance, identifies winners, generates predictive ideas, and delivers them via dashboard — all running on cron.

Use when the user shares a video/concept about content automation, asks to build an "agent that works 24/7", or wants to automate content strategy/ideation.

## Architecture Overview

```
┌─────────────────┐     ┌────────────────┐     ┌─────────────────┐
│  Content Source  │ ──▶ │  Analyzer      │ ──▶ │  Winners/Scores  │
│  (YouTube, CSV)  │     │  muse_analyzer │     │  (heat_score)    │
└─────────────────┘     └────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌────────────────┐     ┌─────────────────┐
│  Cron 24/7      │ ◀── │  Idea Generator│ ◀── │  Winners Data   │
│  cron_run.py    │     │  muse_ideas.py │     │  (winners.json)  │
└─────────────────┘     └────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌────────────────┐     ┌─────────────────┐
│  User wakes up  │ ◀── │  Dashboard     │ ◀── │  Ideas Data     │
│  (dashboard)    │     │  server.py    │     │  (ideas.json)    │
└─────────────────┘     └────────────────┘     └─────────────────┘
```

## Components

### 1. Content Analyzer

Python script that calculates **heat score**:

```
heat_score = (views_norm × 0.4 + engagement_norm × 0.6) × velocity_bonus
```

- **views_norm**: log-scaled views (0-100)
- **engagement**: likes + comments×2 + shares×3, normalized
- **velocity**: views/day since publish, 1x-1.5x bonus

**Data models**: `ContentItem` (id, title, views, likes, comments, shares, published_at, velocity, heat_score), `ContentIdea` (id, title, hook, format, reasoning, score, predictions)

**Input sources**: YouTube Data API v3 (needs API key), CSV import, sample data (`--sample`)

### 2. Idea Generator — LLM Fallback Pattern

**CRITICAL** — always design with graceful degradation:

```python
# Step 1: Build fallback immediately (always works, ~0.1s)
fallback = _generate_fallback_ideas(winners, count)

# Step 2: Try LLM with short timeout (bonus, not requirement)
if api_key and len(api_key) > 10:
    try:
        llm_ideas = call_llm_api(prompt, timeout=8)
        ideas = merge(llm_ideas, fallback)
    except:
        ideas = []

# Step 3: Fallback always safe
return ideas or fallback
```

**Template diversity**: 4 formats (tutorial, comparison, list, storytelling), 10+ topics. Each idea gets score, hook, predictions.

### 3. Dashboard (FastAPI + HTML)

**Routes**:
- `GET /` — HTML dashboard (dark mode, auto-refresh 60s)
- `GET /api/data` — JSON: winners + ideas + stats
- `GET /api/health` — health check
- `POST /api/refresh` — trigger full pipeline
- `POST /api/analyze` / `POST /api/generate-ideas`

**Features**: 4 stat cards, color-coded winner list (green≥70, yellow≥40, gray<40), idea cards with score/hook/format/predictions, pure vanilla JS.

### 4. Cron Runner

Three-phase execution: analyze → generate ideas → write status. Designed to run in <10s.

## Deployment

### Tunnel (cloudflared recommended)
```python
subprocess.Popen(["cloudflared", "tunnel", "--url", f"http://localhost:{port}"],
    stdout=open("tunnel.log", "w"), stderr=subprocess.STDOUT,
    preexec_fn=os.setsid)
# Wait ~12s, grep for https://<random>.trycloudflare.com
```

### Cron (system crontab when Hermes cron CLI unavailable)
```bash
(crontab -l 2>/dev/null; echo "0 6 * * * cd $PWD && python3 cron_run.py >> data/cron.log 2>&1") | crontab -
```

## YouTube Data API Setup

Pierre utilise l'interface française. Voici les libellés exacts :

1. https://console.cloud.google.com → connexion compte Google
2. Menu ☰ → **APIs et services** → **Bibliothèque**
3. Chercher **« YouTube Data API v3 »** → **Activer**
4. Menu ☰ → **APIs et services** → **Identifiants** → **Créer des identifiants** → **Clé API**
5. Une clé apparaît → **Restreindre la clé**
6. **Restrictions relatives aux API** → sélectionner **YouTube Data API v3**
7. (Optionnel) **Restrictions relatives aux adresses IP** → ajouter l'IP du serveur
8. Copier la clé → `export YOUTUBE_API_KEY="***"`
9. Test : `curl -s "https://www.googleapis.com/youtube/v3/videos?part=snippet&id=dQw4w9WgXcQ&key=$YOUTUBE_API_KEY" | head`

**Résolution des handles (@channel) vers channel ID :**

L'API YouTube Data v3 utilise `forHandle` pour résoudre les handles :

```python
# Résoudre @handle → channel ID
r = requests.get("https://www.googleapis.com/youtube/v3/channels",
    params={"part": "id", "forHandle": "@mkbhd", "key": api_key})
channel_id = r.json()["items"][0]["id"]  # → "UCBJycsmduvYEL83R_UJ4riQ"

# Puis rechercher les vidéos
r2 = requests.get("https://www.googleapis.com/youtube/v3/search",
    params={"channelId": channel_id, "part": "snippet", "order": "date",
            "maxResults": 50, "type": "video", "key": api_key})
video_ids = [item["id"]["videoId"] for item in r2.json().get("items", [])]

# Enfin récupérer les stats
r3 = requests.get("https://www.googleapis.com/youtube/v3/videos",
    params={"id": ",".join(video_ids), "part": "statistics,snippet,contentDetails", "key": api_key})
```

**Quota** : 10 000 unités/jour gratuites. Un fetch complet (résolution + search + 50 vidéos) = ~200 unités.

## Pitfalls

- **LLM timeouts**: requests to OpenRouter can hang. Always set `timeout=8` and wrap in try/except. Always build fallback FIRST, LLM as bonus.
- **Cloudflared quick tunnels**: ephemeral — URL changes on restart. Works fine from WSL (serveo.net ne marche pas, timeout).
- **YouTube API**: quota-limited (10k units/day). Use `--sample` for demos.
- **Hermes cron CLI**: `hermes cron list --json` may return non-zero. Fallback to system crontab.
- **serveo.net**: Connection timed out from WSL — ne pas utiliser. cloudflared est le bon tunnel.
- **Dashboard refresh**: 60s frontend polling — pas de websockets nécessaires.
- **YouTube handle extraction**: le `@` dans `@handle` n'est pas capturé par `[\w.-]+` — utiliser un pattern dédié `r'^@([\w.-]+)$'`.

## Quick Start

```bash
python3 muse_analyzer.py --sample   # Generate demo data
python3 muse_ideas.py               # Generate ideas
python3 server.py                   # Dashboard → localhost:8899
cloudflared tunnel --url http://localhost:8899  # Public URL
# Cron 24/7:
(crontab -l 2>/dev/null; echo "0 6 * * * cd $PWD && python3 cron_run.py >> data/cron.log 2>&1") | crontab -
```

## Verification Checklist

- [ ] Analyzer produces `data/winners.json` with heat scores
- [ ] Idea generator produces `data/ideas.json` with 5+ ideas
- [ ] Dashboard serves HTML at `/` (200)
- [ ] API returns JSON at `/api/data`
- [ ] Tunnel URL resolves (200)
- [ ] Cron script runs full pipeline in <10s
- [ ] LLM fallback works without API key (template mode)

## Reference Files
- `references/hermes-oracle-implementation.md` – Hermes Oracle integration guide for the content agent pattern.
- `references/hermes-muse-implementation.md` – Implementation notes for the Hermes Muse analyzer/generator components.
- `references/linkedin-strategy.md` – LinkedIn profile audit, positioning strategy, content segmentation, and post templates.