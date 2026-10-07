---
name: youtube-truecrime-automation
description: "Pipeline YouTube Dark Chronicles: sujets réels mondiaux, bilingue FR/EN, série 2 épisodes/sem."
version: 4.0.0
author: Pierre Andre Erard
platforms: [linux]
tags: [youtube, automation, dark-stories, video, series, bilingual]
---

# YouTube Dark Chronicles — Pipeline Automatisé

Pipeline complet : sujets réels → narration LLM → voix → ambient → clips Pexels → montage → miniature → upload YouTube.
**Série :** 1 sujet = 2 épisodes (mardi + jeudi), cliffhangers, bilingue FR/EN, planification auto.

## Usage

```bash
cd /root/projets/youtube-automation && python3 main.py

# Générer les scripts (test)
python3 -m modules.series_real

# Pipeline complet
python3 main.py                          # Mode standalone
python3 main.py --series                 # Mode série (2 épisodes fictifs suisses, LEGACY)
python3 main.py --upload                 # + upload
python3 weekly_series.py --dry-run       # Vérifier les dates
```

## Architecture du Pivot (v4)

| Composant | Fichier | Rôle |
|-----------|---------|------|
| **BDD sujets réels** | `data/subjects.py` | 30 sujets mondiaux célèbres, faits vérifiés FR+EN |
| **Générateur réel** | `modules/series_real.py` | Narration via Gemini 2.5-flash, fallback template |
| Voix | `modules/voice.py` | edge-tts (fr-FR-Denise / en-US-Christopher) |
| Ambient | `modules/ambient.py` | Brown noise + reverb ffmpeg |
| Visuels | `modules/visuals.py` | Clips Pexels réels |
| Vidéo | `modules/video.py` | ffmpeg assemblage |
| Upload | `modules/upload_youtube.py` | OAuth + publishAt |
| Legacy fictif | `modules/series.py`, `script.py` | Sujets suisses fictifs (conservé) |

## Sujets réels (catégories)

- 🔪 Crimes célèbres : Zodiac, Jack l'Éventreur, Dahlia Noir, Bundy, Dahmer, Pándy, Grégory, Ligonnès, Unterweger, Moors Murders, Villisca, Hinterkaifeck
- 🕳️ Disparitions : MH370, D.B. Cooper, Roanoke, Earhart, Sodder, Mittank, Froon, Mary Celeste
- 🌊 Catastrophes : Tchernobyl, Titanic, Triangle des Bermudes, Halifax, Pompéi, Peshtigo
- 👁️ Mystères : Signal Wow, Voynich, Oumuamua, Hessdalen, Atlantide, Versailles, Dyatlov, Somerton, Alcatraz, Oak Island, Kryptos, Toynbee, Toungouska

## Narration LLM (Gemini)

- Modèle : `gemini-2.5-flash` via API Google (gratuit)
- Clé : GOOGLE_API_KEY dans /root/.hermes/.env (⚠️ 4 occurrences — prendre celle commençant par AIza, ignorer les placeholders "your_google...")
- Règle : les faits de la BDD sont sacrés, le LLM ne fait que styliser
- Longueur cible : 800-1000 mots/épisode
- Fallback : template faits bruts si API KO ou réponse trop courte

## Planification

- Cron mardi 06:00 → `weekly_series.py`
- P1 mardi 12h, P2 jeudi 12h (publishAt, private)
- Logs : output/cron.log

## Compte YouTube

pierre.business53@gmail.com, projet GCloud `poste-youtube-505016`, token `output/youtube_token.pickle`. monsunrise@gmail.com = SUSPENDU (ne pas utiliser).

## Repo GitHub

https://github.com/SupermaxiMarket/youtube-truecrime-automation