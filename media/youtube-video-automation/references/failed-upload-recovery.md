# Failed Upload Recovery — après `invalid_grant`

Quand le cron log montre `google.auth.exceptions.RefreshError: invalid_grant:
Token has been expired or revoked.`, les vidéos sont **générées sur disque mais
jamais uploadées**. Ce document donne la procédure exacte après avoir récupéré
l'auth (voir `references/youtube-oauth-upload.md` → « Récupération après expiration »).

## 1. Identifier les épisodes morts dans le cron log

```bash
grep -n "ÉPISODE\|upload_to_youtube\|RefreshError\|invalid_grant\|upload\|video_" \
  /root/projets/youtube-automation/output/cron.log | tail -60
```

Marqueurs :
- `✓ Vidéo finale : ...video_XXXX.mp4` = vidéo assemblée sur disque
- `refresh_expired|invalid_grant` ≈ 3 lignes après = échec upload
- `⏰ Publication planifiée` juste avant = la date qui était prévue

**Repère :** les vidéos existent si le log montre `✓ Vidéo finale` et `✓ Pipeline terminé`
juste avant l'erreur YouTube.

## 2. Localiser les fichiers vidéo

```bash
ls -la /root/projets/youtube-automation/output/videos/video_*.mp4
```

Chaque vidéo fait ~80–130 MB. Les épisodes non uploadés ont leur fichier
sur disque mais aucune URL dans `series_state.json`.

## 3. Upload manuel des vidéos en attente

```bash
cd /root/projets/youtube-automation

# Vérifier que le token est valide d'abord
python3 -c "
import pickle
with open('output/youtube_token.pickle','rb') as f:
    creds = pickle.load(f)
print(f'Valid: {creds.valid}, Expired: {creds.expired}')
"

# Uploader UNE vidéo spécifique (trouver le titre dans le cron.log)
python3 -c "
import sys; sys.path.insert(0, '.')
from modules.upload_youtube import upload_video
from modules.script import load_script

vid_path = 'output/videos/video_XXXX.mp4'
title = 'Titre exact depuis le cron.log'  # copier depuis le log
desc = 'Description...'
thumbnail = vid_path.replace('videos/', 'thumbnails/').replace('.mp4', '.jpg')

result = upload_video(vid_path, title, desc, thumbnail,
                     publish_at='2026-09-08T12:00:00+02:00')
print(result)
"
```

## 4. Ajuster series_state.json après upload manuel

```python
import json
# Charger + ajouter l'entrée manquante
state = json.load(open("output/series_state.json"))
state["history"].append({
    "topic": "...",
    "episodes": [7, 8],           # next_episode, next_episode+1
    "date": "2026-09-08T06:00:00",
    "urls": {
        "part1": "https://youtube.com/watch?v=...",  # URL de l'upload manuel
        "part2": "..."  # si uploadé
    }
})
state["next_episode"] = 9 + 1
json.dump(state, open("output/series_state.json", "w"), indent=2)
```

## 5. Test de connexion rapide avant de lancer un pipeline

```python
from googleapiclient.discovery import build
import pickle
creds = pickle.load(open("output/youtube_token.pickle", "rb"))
youtube = build("youtube", "v3", credentials=creds)
# videos().list échoue (pas le bon scope), mais thumbnails.set sans body confirme l'auth
try:
    youtube.thumbnails().set(videoId="dummy").execute()
except Exception as e:
    if "dummy" in str(e) or "404" in str(e) or "mediaBody" in str(e):
        print("✅ Auth OK — token valide")
    else:
        print("❌ Auth KO —", e)
```

## 6. Empêcher la récidive (surveillance)

Ajouter une vérification de validité du token DANS le cron avant de lancer
le pipeline lourd. Dans `weekly_series.py` ou `main.py`, au début :

```python
import pickle, os
token_path = "output/youtube_token.pickle"
if os.path.exists(token_path):
    creds = pickle.load(open(token_path, "rb"))
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        if creds.expired:
            print("❌ TOKEN EXPIRÉ — impossible de rafraîchir. Pipeline annulé.")
            sys.exit(1)
```