## ffmpeg `-c copy` concat bug — silent truncation

Découvert le 09/09/2026 sur le pipeline YouTube Dark Chronicles.

### Symptôme

Le module `video.py` concatène des clips normalisés en boucle avec `-c copy` pour
couvrir la durée audio, mais la vidéo finale est **silencieusement tronquée** :
- 298s d'audio → 86s de vidéo finale (avec `-shortest`)
- 290s d'audio → 132s de vidéo finale
- Aucune erreur ffmpeg dans les logs

### Cause

`-c copy` ne retimestamps pas les clips concaténés. Si les clips normalisés ont
des timestamps internes différents (PTS/DTS), le résultat peut faire sauter des
périodes entières. Le fichier concat fait la bonne taille (looped), mais la
lecture est accélérée/tronquée.

### Fix 1 — Re-encode pendant le concat

Remplacer `-c copy` par `-c:v libx264 -preset fast -crf 23` dans la commande
de concat boucle :

```python
# BROKEN
cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
       "-i", concat_list, "-c", "copy", temp_loop]

# FIXED
cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
       "-i", concat_list,
       "-c:v", "libx264", "-preset", "fast", "-crf", "23",
       temp_loop]
```

Le re-encode est plus lent mais garantit une sortie correcte.

### Fix 2 — `-stream_loop` sur vidéo déjà assemblée

Quand une vidéo existe déjà mais est trop courte (bug déclenché), on peut la
réparer sans refaire tout le pipeline :

```bash
ffmpeg -y -stream_loop N -i short_video.mp4 -i audio.mp3 \
  -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k \
  -shortest -map 0:v:0 -map 1:a:0 -movflags +faststart output.mp4
```

Où N = ceil(durée_audio / durée_vidéo) + 1.

Avantage : utilise la vidéo buggée comme une boucle de clips propre, évite
le concat et ses problèmes de timestamp.

### Clip normalization (préventif)

Tous les clips DOIVENT être normalisés AVANT tout concat :
- Résolution : 1920×1080 (avec padding letterbox)
- Framerate : 30 fps
- Codec : libx264
- Son : désactivé (`-an`)

Même avec normalisation, `-c copy` peut échouer si les clips originaux ont
des keyframe intervals différents. Préférer `-stream_loop` ou re-encode.