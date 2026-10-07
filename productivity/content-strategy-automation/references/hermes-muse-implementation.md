# Hermes Muse — Implémentation de référence

Projet concret construit le 2026-08-09 basé sur la vidéo "I built an AI employee called Hermes" (https://youtu.be/G5kdBlpEQvw)

## Emplacement

`/root/projets/hermes-muse/`

## Structure

```
hermes-muse/
├── muse_analyzer.py       # Analyse + heat score + winners
├── muse_ideas.py          # Génération d'idées avec fallback template
├── cron_run.py            # Script cron 3 phases
├── server.py              # FastAPI dashboard (port 8899)
├── templates/
│   └── dashboard.html     # Dark mode, auto-refresh 60s, 4 stat cards
├── data/
│   ├── latest_analysis.json  # Dernière analyse
│   ├── winners.json          # Winners triés par heat score
│   ├── ideas.json            # Idées générées
│   ├── cron.log              # Log du cron
│   ├── server.log            # Log du serveur
│   ├── tunnel.log            # Log cloudflared
│   ├── status.json           # Statut du dernier run
│   └── public_url.txt        # Dernière URL publique
└── setup.py               # Installation automatisée
```

## État actuel

- **Dashboard**: http://localhost:8899 (PID 6820)
- **Tunnel public**: https://aqua-cycling-sarah-newspaper.trycloudflare.com
- **Cron**: `0 6 * * *` (06:00 quotidien, system crontab)
- **Données**: 10 items sample, 5 idées générées

## Commandes utiles

```bash
# Voir les logs
tail -f /root/projets/hermes-muse/data/cron.log
tail -f /root/projets/hermes-muse/data/server.log

# Relancer l'analyse
python3 /root/projets/hermes-muse/muse_analyzer.py --sample

# Re-générer les idées
python3 /root/projets/hermes-muse/muse_ideas.py

# Relancer le dashboard
pkill -f server.py; python3 /root/projets/hermes-muse/server.py &

# Relancer le tunnel
pkill -f cloudflared.*8899
cloudflared tunnel --url http://localhost:8899 > /root/projets/hermes-muse/data/tunnel.log 2>&1 &

# Tester le cron
python3 /root/projets/hermes-muse/cron_run.py
```

## Métriques de perf

- Analyse + génération d'idées: < 1s (sans LLM API)
- Démarrage dashboard: ~3s
- Tunnel cloudflared: ~12s pour obtenir l'URL
- Cron complet: ~5s