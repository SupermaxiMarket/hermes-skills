# Vérifier le statut de publication YouTube (oEmbed API)

Quand une vidéo est uploadée en `private` avec `publishAt`, la publication
automatique de YouTube peut échouer silencieusement. Cette ref donne la
méthode sans auth pour vérifier si une vidéo est réellement publique.

## API oEmbed (sans auth — gratuit, pas de quota)

```python
import requests

def check_video(video_id: str) -> str:
    """Retourne 'public', 'private/unlisted', ou 'error'."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        return "public"
    elif r.status_code == 403:
        return "private/unlisted"
    else:
        return f"error ({r.status_code})"
```

### Codes réponse

| Code | Signification |
|------|---------------|
| 200  | ✅ **Public** — la vidéo est accessible, `r.json()["title"]` donne le titre |
| 403  | ⏳ **Privée ou non listée** — pas encore publique, ou configurée en `private`/`unlisted` |
| 404  | ❌ **Introuvable** — l'ID n'existe pas ou la vidéo a été supprimée |
| 401  | ⚠️ **Restreinte** — vidéo privée sur une chaîne avec restrictions d'âge |

### Exemple de diagnostic complet

```python
videos = [
    ("abc123", "Mon Épisode P1"),
    ("def456", "Mon Épisode P2"),
]
for vid, name in videos:
    r = requests.get(
        f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json",
        timeout=10
    )
    if r.status_code == 200:
        print(f"{name}: ✅ PUBLIÉ — {r.json()['title']}")
    elif r.status_code == 403:
        print(f"{name}: ⏳ PRIVÉ — pas encore public")
    else:
        print(f"{name}: {r.status_code}")
```

## Piège : Part 2 pas visible immédiatement

Dans le workflow série, Part 1 est programmé le **même jour à 12:00** et
Part 2 est programmé **+2 jours à 12:00** (jeudi pour un run mardi).

Quand l'utilisateur dit « je ne vois pas la vidéo sur la chaîne » :
1. Vérifier le `publishAt` dans le cron.log — si c'est dans le futur, la vidéo
   est encore privée (normal)
2. Lancer oEmbed check pour confirmer que Part 1 est bien passée en public
3. Si Part 1 est 403 aussi → le scheduling a peut-être raté → vérifier le
   statut dans YouTube Studio

## Quand le scheduling rate

Si oEmbed retourne 403 pour Part 1 alors que `publishAt` est passé :
- YouTube peut rater le scheduling sans notification
- Solution : uploader une update via l'API (`videos().update()` avec
  `privacyStatus="public"`) OU passer manuellement en public depuis YouTube Studio
- `publishAt` est un one-shot — YouTube n'essaie pas de ré-publier si raté