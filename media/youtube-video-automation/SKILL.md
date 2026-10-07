---
name: youtube-video-automation
description: "Use when building faceless YouTube video pipelines."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
tags: [youtube, automation, faceless, tts, ffmpeg, content-creation]
related_skills: [video-slideshow, youtube-content]
---

# YouTube Video Automation Pipeline

Build faceless YouTube channels with AI: script generation → TTS voiceover → images → ffmpeg video assembly → thumbnail → (future) upload.

## Architecture

```
main.py (orchestrator)
  ├── modules/script.py     # Generate scripts (template-based or LLM)
  ├── modules/voice.py      # TTS via edge-tts (free, French voices)
  ├── modules/visuals.py    # Download images + cinematic filters
  ├── modules/video.py      # ffmpeg assembly + subtitles
  └── modules/thumbnail.py  # YouTube thumbnail (1280x720, dark style)
```

## Quick Start

```bash
cd /root/projets/youtube-automation

# Full pipeline (generates everything)
python3 main.py

# Custom topic
python3 main.py --topic "L'Affaire du Disparu — Un Cold Case"

# Script only
python3 main.py --script-only

# Resume from existing script
python3 main.py --resume output/scripts/20260812_*.txt
```

## Module Details

### Script (`modules/script.py`)
- Template-based (no LLM needed): 30+ true crime Swiss/French topics
- Generates ~1150-1200 words (~8 min video) with narrative arc
- Each section has an `[IMAGE: description]` prompt for visuals
- Output format: `TITLE: ...\n---\nbody` (metadata delimited by `---`)
- LLM backend possible via OpenRouter (Nemotron 550B free, etc.) — patch `config.yaml`
- **Parsing pitfall**: split(`---`) produces 3 parts; clean text is parts[2:] when metadata present

### Voice (`modules/voice.py`)
- Uses `edge-tts` (Microsoft Edge TTS): free, natural French voices
- Best voices: `fr-FR-DeniseNeural`, `fr-FR-HenriNeural`, `fr-FR-CharlineNeural`
- Rate `+5%` works well for narration

### Visuals (`modules/visuals.py`)
- Downloads from picsum.photos (free, no API key)
- Cinematic filter: brightness 0.6, saturation 0.7, contrast 1.3, Gaussian blur 1px, letterbox
- Resolves to 1920×1080

### Video (`modules/video.py`)
- ffmpeg concat of images with `-shortest` (audio-driven duration)
- Filters: scale, pad with dark background, format yuv420p
- Subtitles via `subtitles=` filter (Georgia font, white, shadow)
- h264 + aac output, ~17MB for 7min video

### Thumbnail (`modules/thumbnail.py`)
- 1280×720, dark cinematic style
- Title overlay (max 4 lines, centered)
- Red accent bar, letterbox bands

## Python Dependencies

```bash
pip install edge-tts moviepy pillow pyyaml requests
```

## TTS — Free Options

| Engine | Quality | French | Cost |
|--------|---------|--------|------|
| edge-tts (Microsoft) | ★★★★☆ | Excellent (Denise, Henri) | Free |
| gTTS (Google) | ★★☆☆☆ | Correct | Free |
| ElevenLabs | ★★★★★ | Excellent | Paid (10k free chars/mo) |
| OpenAI TTS | ★★★★☆ | Good | Paid |

## Pitfalls

- **`-c copy` concat bug** — When looping clips via ffmpeg concat with `-c copy` to cover audio duration, the output is silently truncated if clips have non-homogeneous codecs/timestamps (298s audio → 86s output). **Fix**: re-encode the loop concat with `-c:v libx264 -preset fast -crf 23`. See `references/ffmpeg-concat-pitfall.md` for full reproduction and the `-stream_loop` workaround.

- **Ollama cloud models** (`glm-5.2:cloud`, `deepseek-v4-flash:0731-cloud`) are **paywalled** since Aug 2026 — use template-based script gen or OpenRouter free models
- **edge-tts**: pip-install only; no other setup
- **Word count**: target ~1150-1500 words for 8-10 min (YouTube monetization)
- **Metadata parsing**: script files use `TITLE:\n---\nbody` — parse with 3-part `split("---")`
- **Large model pulls**: local Ollama models (4-30GB) may timeout in sandbox environments
- **YouTube thumbnail 403** — custom thumbnails return `403 forbidden` with message `"The authenticated user doesn't have permissions to upload and set custom video thumbnails"`. This affects new channels (<48h) AND channels still in probation (first ~3-5 uploads even on phone-verified accounts). Symptom: videos upload fine, thumbnails fail. YouTube falls back to auto-thumbnail. The restriction lifts automatically after enough uploads/age. Workaround: retry the thumbnail set endpoint after each upload. Also 1-second silent test videos get "processing abandoned".
- **OAuth token expiry (`invalid_grant`)** — après une période d'inactivité (~6 mois), le refresh_token YouTube expire et l'upload explose sur `next_chunk()` avec `google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked.`. Le pipeline génère tout parfaitement (script → voix → clips → montage → thumbnail) mais le crash arrive pendant l'upload. **Ne pas gaspiller CPU/disque si on peut pas uploader** — vérifier le token AVANT de lancer un pipeline lourd. Solution complète dans `references/youtube-oauth-upload.md` → section « Récupération après expiration ». Points-clés : (1) réutiliser le projet Google Cloud existant — ne PAS en créer un nouveau, (2) supprimer l'ancien .pickle, (3) régénérer l'URL d'auth sans PKCE, (4) s'assurer que l'API est activée et l'email dans les test users avant d'ouvrir l'URL. Après récupération, voir `references/failed-upload-recovery.md` pour uploader les vidéos laissées sur disque.

  ⚠️ **Délai réel constaté** : le refresh token peut mourir en ~6 jours, pas seulement après des mois. Si le token valide un mardi est déjà mort le mardi suivant, vérifier dans les paramètres de sécurité du compte Google si l'accès a été révoqué manuellement. Aussi, le fichier `youtube_token.pickle` peut **disparaître purement et simplement** du dossier `output/` — pas seulement expirer. Toujours vérifier son existence avant de lancer le pipeline :
  ```python
  import os
  TOKEN_PATH = "output/youtube_token.pickle"
  if not os.path.exists(TOKEN_PATH):
      print("❌ TOKEN ABSENT — pipeline annulé. Lancer reauth_youtube.py")
      sys.exit(1)
  ```
- **Compte Google mismatch** — le token OAuth est lié au compte Google qui possède la chaîne YouTube, PAS au compte admin du projet Google Cloud. Si l'URL d'auth affiche « Service non disponible pour votre compte » ou « Erreur 403: access_denied », le navigateur est connecté avec le mauvais compte OU le projet Google Cloud n'a pas l'API activée / l'email dans les test users. Ouvrir en navigation privée pour forcer le choix du compte, et vérifier la console avant.

- **Vidéo pas visible sur la chaîne après upload programmé** — le workflow série upload en `private` avec `publishAt`. Part 1 est programmé le mardi 12:00, Part 2 le **jeudi 12:00** (+2 jours). Si l'utilisateur dit « je ne vois pas la vidéo », vérifier : (1) `publishAt` dans le cron.log — si futur, normal qu'elle soit privée, (2) utiliser l'API oEmbed (sans auth, `GET https://www.youtube.com/oembed?url=...&format=json` → 200 = public, 403 = privé) pour confirmer le statut. Si Part 1 est encore 403 après l'heure programmée, YouTube a raté le scheduling — solution : passage en public via l'API `videos().update(privacyStatus="public")` ou YouTube Studio. Voir `references/verify-publish-status.md`.

## Narration via Gemini 2.5 Flash (gratuit, fiable)

Pour enrichir des faits vérifiés en narration thriller (les faits restent sacrés, le LLM ne fait que styliser) :

```python
resp = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
    headers={"x-goog-api-key": key, "Content-Type": "application/json"},
    json={
        "contents": [{"parts": [{"text": system + "\n\n" + user}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.8,
            "thinkingConfig": {"thinkingBudget": 0},  # OBLIGATOIRE — voir pitfall
        },
    }, timeout=120)
```

### Pitfalls Gemini

- **`thinkingConfig` DOIT être dans `generationConfig`** — au niveau racine du JSON, l'API renvoie 400 `Unknown name "thinkingConfig"`.
- **Sans `thinkingBudget: 0`, les tokens de réflexion mangent `maxOutputTokens`** : le texte s'arrête à ~90-130 mots avec `finishReason=MAX_TOKENS` alors que 4000 tokens devraient suffire pour 1300 mots. Symptôme : réponses "trop courtes" inexpliquées.
- **Modèles retirés** : `gemini-2.0-flash` et `gemini-2.5-pro` renvoient 404 (`no longer available`). Utiliser `gemini-2.5-flash`.
- **.env avec plusieurs GOOGLE_API_KEY** : filtrer les valeurs commençant par `AIza` et exclure celles contenant `your_` (placeholders du template d'install). Prendre la dernière valide.
- **Contrainte de longueur** : demander « N paragraphes de minimum X mots PAR FAIT » est suivi beaucoup plus fidèlement que « 1100 mots au total ».

### Style de narration vidéo (préférence Pierre)

- **Première phrase : un fait choc** (date, chiffre, nom) — « 239 vies. Évaporées. Le 8 mars 2014. » PAS de préambule philosophique (« il est des histoires... »). Pierre rejette les intros lentes : « trop long sans rien à dire ».
- Interdire explicitement les indications de production entre parenthèses (musique, lumière, sons) — le texte est lu par une voix off.
- Phrases courtes dominantes, chaque phrase doit faire avancer le récit.

## YouTube Shorts (trafic)

Générer un Short 9:16 depuis un épisode 16:9 — extraire les ~45-50 dernières secondes (climax/cliffhanger) et recadrer :

```bash
ffmpeg -ss <start> -i episode.mp4 -t 50 \
  -vf "crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" \
  -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k short.mp4
```

- Uploader en **public** (les Shorts doivent être publics pour entrer dans le feed)
- Titre putaclic + `#shorts` ; description = lien vers l'épisode complet
- Le Short ramène les visiteurs vers l'épisode unlisted/long

## Series Workflow (cron-driven, multi-episode)

For a channel pushing 1 case/week split into 2 parts, use `weekly_series.py` + cron:

```bash
# Cron: Tuesday 06:00
0 6 * * 2 cd /root/projets/youtube-automation && /usr/bin/python3 weekly_series.py >> output/cron.log 2>&1
```

### Scheduling logic (`weekly_series.py`)

- Normal mode (Tuesday): Part 1 publishes **today 12:00**, Part 2 **Thursday 12:00**
- Catch-up mode (any other day with `--now`): Part 1 **tomorrow 12:00**, Part 2 **+2 days 12:00**
- Uploads as `privacy="private"` with `publishAt` RFC 3339 timestamp — YouTube schedules the publication
- Use `--dry-run` to preview dates without executing

### Series state (`output/series_state.json`)

```json
{
  "season": 1,
  "next_episode": 3,
  "history": [
    {
      "topic": "...",
      "episodes": [1, 2],
      "date": "2026-08-18T06:03:07.378252",
      "urls": {
        "part1": "https://youtube.com/watch?v=...",
        "part2": "https://youtube.com/watch?v=..."
      }
    }
  ]
}
```

- `next_episode` auto-increments after each successful run
- History stores URLs for reference
- The series runner (`series_real.py`) picks the next subject from `data/subjects.py` using the counter

### Launch a single episode

For testing or ad-hoc releases, `launch_episode.py <subject_id> <lang>`:
Full pipeline (script → TTS → ambient → visuals → video → thumbnail → upload). Defaults: `subject_id=zodiac`, `lang=fr`, uploads as `unlisted`. Pass `--privacy public` for immediate release.

## References

- `references/youtube-oauth-upload.md` — OAuth Desktop depuis WSL (setup + recovery)
- `references/ffmpeg-concat-pitfall.md` — `-c copy` concat bug: silent truncation when looping clips, fix via re-encode or `-stream_loop`
- `references/series-scheduling.md` — compute_publish_times details and cron setup
- `references/verify-publish-status.md` — Vérifier si une vidéo uploadée est réellement publique (oEmbed API, sans auth)
- `references/failed-upload-recovery.md` — récupération après `invalid_grant` : uploader les vidéos laissées sur disque, ajuster series_state.json
- `scripts/reauth_youtube.py` — script de ré-auth manuelle (supprime token → URL → échange → sauvegarde)
- `video-slideshow` — simpler ffmpeg slideshow tool
- `youtube-content` — YouTube transcript extraction