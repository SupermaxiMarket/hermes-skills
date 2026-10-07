# Hermes Oracle — External Trend Scanning

Implémentation de référence pour le scan de tendances multi-sources (Hermes Oracle), construite le 2026-08-20 d'après la vidéo "Top 10 Hermes Agent Skills" (Julian Goldie).

## Emplacement

`/root/projets/agent-os/hermes-oracle/oracle.py`

## Architecture

```
oracle.py
├── --scan       → fetch_trends_from_sources() → score → save
├── --serve      → Dashboard web (port 8768)
├── --cron       → Scan + log vers Obsidian vault
└── --history    → Afficher l'historique des scans
```

## Sources de tendances

1. **Google News RSS** (FR/CH) — `news.google.com/rss/topics/...?hl=fr&gl=CH`
2. **Hacker News API** — `hacker-news.firebaseio.com/v0/` (top 10 stories)
3. **Fallback FR** — 8 sujets IA/marketing/SEO/Suisse pour fiabilité

## Scoring

```
score = 50 (base)
       + 5 par mot-clé boost (IA, marketing, SEO, LinkedIn, ...)
       + 10 si ≥3 mots communs avec une autre source (fréquence)
       → cap à 100
```

Catégorisation auto: IA & Tech, Marketing Digital, Business, Suisse, Productivité, Général.

## Dashboard

```bash
python3 oracle.py --serve      # → http://localhost:8768
```

Routes:
- `GET /` — HTML dark dashboard (cards, barres de score, idées)
- `GET /api/data` — JSON (trends + ideas + history)
- `GET /api/scan` — Déclencher un scan

Rafraîchissement automatique 60s.

## Guide Machine (intégration)

Le Guide Machine transforme les idées en pages HTML déployables:

```bash
python3 /root/projets/agent-os/guide-machine/guide_builder.py "Sujet" --keywords "tags"
```

Guide produit: HTML stylisé (hero, TOC, steps, callouts, CTAs), serveur web (port 8767).

## Agent OS Launch Center

```bash
python3 /root/projets/agent-os/launch.py
  --start    → Lance Oracle (8768) + Guide Machine (8767)
  --stop     → Arrête tout
  --status   → État des services
  --cron     → Cycle complet: scan + log vers vault Obsidian
```

## File d'attente

Les résultats de scan sont copiés vers `~/obsidian-vault/AgentOS/Logs/<timestamp>-oracle-*.json`
Cron configuré à 06:00 quotidien (crontab).

## Pitfalls

- **Google News RSS**: parfois lent (15s timeout). Le fallback FR garantit des résultats même si RSS échoue.
- **HN API**: gratuite mais rate-limitée. Limiter à 10 stories max.
- **Tunnel cloudflared**: URL change à chaque redémarrage.
- **Dashboard**: serveur HTTP simple (pas FastAPI) — suffisant pour un usage local.