---
name: youtube-api-upload
description: "Upload videos to YouTube via Data API v3 + OAuth 2.0."
version: 1.0.0
author: Pierre Andre Erard
platforms: [linux]
tags: [youtube, upload, oauth, google-cloud, api]
---

# YouTube API Upload (OAuth 2.0 + Data API v3)

Upload programmatique de vidéos sur YouTube via l'API Google, avec auth OAuth 2.0
fonctionnant en environnement headless (WSL / serveur sans navigateur).

## Prérequis Python

```bash
pip install --break-system-packages \
  google-api-python-client google-auth-oauthlib google-auth-httplib2
```

## Créer les identifiants (une seule fois)

### Prérequis — API YouTube activée

1. https://console.cloud.google.com → créer ou sélectionner le projet
2. Activer "YouTube Data API v3" : https://console.cloud.google.com/apis/library/youtube.googleapis.com
3. Cliquer **ENABLE**

### Écran de consentement OAuth

https://console.cloud.google.com/auth/branding

| Champ | Valeur |
|-------|--------|
| **App name** | ex. "Dark Chronicles" |
| **Email support** | l'email du compte YouTube (pierre.business53@gmail.com) |
| **Page d'accueil** | `https://www.youtube.com/` (ou l'URL de la chaîne) |
| **Politique de confidentialité** | `https://www.youtube.com/` |
| **Domaines autorisés** | `youtube.com` (sans https://, sans www) |
| **Logo** | optionnel |

Scopes → **ADD OR REMOVE SCOPES** → chercher `youtube.upload` → ajouter.
Test users → **ADD USERS** → ajouter l'email du compte YouTube.

⚠️ Propagation : 5 min à quelques heures pour que les changements de l'écran
de consentement soient effectifs.

### Créer le client OAuth — Application Web (pas Desktop !)

Google a **déprécié le flux OOB (out-of-band)** en 2023-2024. L'URI
`urn:ietf:wg:oauth:2.0:oob` renvoie une erreur. Il faut utiliser un **client
"Application Web"** avec **URI de redirection**.

1. https://console.cloud.google.com/apis/credentials
2. **+ CRÉER DES IDENTIFIANTS** → **ID client OAuth**
3. Type : **Application Web**
4. Nom : ex. "Dark Chronicles Web"
5. **URI de redirection autorisés** → **AJOUTER UN URI** → `http://127.0.0.1:8080`
6. **CRÉER** → copier l'ID client et le secret (format `GOCSPX-...`)

Ne PAS utiliser le type "Application de bureau" (Desktop) — il n'a pas le
champ redirect URI et ne peut pas utiliser le flux local.

### Récupérer client_secret.json

Télécharger le JSON depuis la page du client OAuth (bouton en haut), OU
créer manuellement au format `{"web":{"client_id":"...","client_secret":"...",
"redirect_uris":["http://127.0.0.1:8080"]}}` — voir `templates/client_secret_web.json`.

## Flow OAuth en headless (WSL) — serveur local

⚠️ **Le flux OOB (`urn:ietf:wg:oauth:2.0:oob`) ne fonctionne plus** —
Google renvoie "Service non disponible" ou "Accès bloqué : la demande de cette
appli n'est pas valide". Utiliser un serveur HTTP local sur 127.0.0.1 avec un
client **Application Web** (voir Créer les identifiants ci-dessus).

### Code — serveur local de capture

```python
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from google.oauth2.credentials import Credentials
import requests, json, pickle, os, webbrowser

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
PORT = 8080
REDIRECT_URI = f"http://127.0.0.1:{PORT}"

auth_code = None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in qs:
            auth_code = qs["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"✅ Authentification reussie !")
            self.server.shutdown()

server = HTTPServer(("127.0.0.1", PORT), Handler)

auth_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?response_type=code&client_id={cid}"
    f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
    f"&scope={urllib.parse.quote(SCOPES[0])}"
    "&access_type=offline&prompt=consent"
)
print(f"🔗 Ouvrir: {auth_url}")
webbrowser.open(auth_url)
server.serve_forever()

# Échange code → token
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": auth_code, "client_id": cid, "client_secret": csecret,
    "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code",
}, timeout=30)
data = resp.json()
creds = Credentials(token=data["access_token"],
    refresh_token=data.get("refresh_token"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=cid, client_secret=csecret, scopes=SCOPES)
with open("youtube_token.pickle", "wb") as f:
    pickle.dump(creds, f)
```

### Access & Refresh Token

L'URL d'auth DOIT contenir `access_type=offline&prompt=consent` pour obtenir
un **refresh_token** — sans lui, l'access_token expire au bout d'1 heure et
il faut refaire toute l'auth. Avec le refresh_token, les credentials se
rafraîchissent automatiquement via `google.oauth2.credentials.Credentials`.

### WSL + Chrome Windows — ça marche

Contrairement à une idée reçue, le redirect vers `http://127.0.0.1:PORT`
fonctionne entre Chrome (Windows) et un serveur HTTP lancé dans WSL — à
condition d'utiliser un **client Application Web** avec `redirect_uris` bien
configurés. Si l'erreur `redirect_uri_mismatch` apparaît, attendre la
propagation Google (5 min → quelques heures).

### Alternative — code en argument

Si le serveur local est compliqué (pare-feu, etc.), on peut aussi obtenir
manuellement le code via le navigateur, puis le passer au script :

```python
import requests
code = input("Colle le code > ").strip()
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": code, "client_id": cid, "client_secret": csecret,
    "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code",
}, timeout=30)
```

Mais le serveur local est plus simple pour l'utilisateur (pas de copier-coller).

## Pièges courants

**"Accès bloqué / Erreur 403 access_denied"** — l'app est en mode test et l'email
Google n'est pas testeur. Fix : Écran de consentement OAuth → section "Testeurs"
(Test users) → ajouter l'email. ⚠️ Propagation : 5 min à quelques heures.

**"app non vérifiée"** — normal en mode test. Cliquer "Paramètres avancés" →
"Accéder à [nom-du-projet]" pour passer.

**Les clients OAuth inactifs** sont supprimés après 6 mois sans utilisation
(notification envoyée, restauration possible 30 jours).

## Piège — OOB déprécié (2026)

Google a déprécié le flux OOB (`urn:ietf:wg:oauth:2.0:oob`). Ne pas l'utiliser.
Il renvoie "Service non disponible" ou `redirect_uri_mismatch`. Utiliser le
flux serveur local avec client "Application Web" (voir section ci-dessus).

## Miniature — Erreur 403 "forbidden" sur thumbnails().set()

`youtube.thumbnails().set()` retourne `403 The authenticated user doesn't have
permissions to upload and set custom video thumbnails` si le compte n'a pas
le badge de vérification de chaîne (ou une ancienne condition de vérification).
C'est un flag YouTube, pas une config OAuth — l'API ne peut pas le contourner.

Solutions :
1. **Uploader la miniature manuellement** depuis YouTube Studio → l'API l'accepte
   après coup si la chaîne est éligible
2. **Ne pas setter de miniature automatique** — laisser YouTube générer une
   capture d'écran (mieux que rien)
3. Vérification de chaîne (https://support.google.com/youtube/answer/3351)
   débloque cette API pour le compte

## client_secret.json — format Web Application

Pour un client "Application Web" :

```json
{"web":{
  "client_id":"537222562519-xxxxx.apps.googleusercontent.com",
  "project_id":"le-nom-du-projet",
  "auth_uri":"https://accounts.google.com/o/oauth2/auth",
  "token_uri":"https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
  "client_secret":"GOCSPX-...",
  "redirect_uris":["http://127.0.0.1:8080"],
  "javascript_origins":["http://127.0.0.1:8080"]
}}
```

Le champ `redirect_uris` DOIT correspondre exactement à ce qui est enregistré
dans la Console Google. Le champ `javascript_origins` est optionnel mais
recommandé.

## Sécurité (obligatoire)

- `client_secret.json` et le token pickle DOIVENT être dans `.gitignore` —
  jamais committer les secrets OAuth sur un repo public.
- Le token pickle donne un accès complet à la chaîne YouTube : même traitement.

## Upload resumable (résistant aux coupures)

```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

youtube = build("youtube", "v3", credentials=credentials)
body = {
    "snippet": {"title": "...", "description": "...", "tags": [...],
                "categoryId": "27", "defaultLanguage": "fr"},
    "status": {"privacyStatus": "unlisted",  # public | unlisted | private
               "selfDeclaredMadeForKids": False, "madeForKids": False},
}
media = MediaFileUpload(video_path, mimetype="video/mp4",
                        chunksize=5*1024*1024, resumable=True)
request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
response = None
while response is None:
    status, response = request.next_chunk()  # retry sur 500/502/503/504
video_id = response["id"]
```

Miniature : `youtube.thumbnails().set(videoId=..., media_body=MediaFileUpload(img, mimetype="image/jpeg"))`.

## Fichiers

- `templates/client_secret.json` — format "installed" prêt à remplir.
- `templates/client_secret_web.json` — format "web" pour client Application Web
  (recommandé, OOB déprécié).
- `references/oauth-erreurs-2026.md` — diagnostics des erreurs OAuth Google
  rencontrées (redirect_mismatch, OOB bloqué, test users manquant, etc.).
