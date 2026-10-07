# YouTube Data API v3 — Upload OAuth depuis WSL (headless)

## Projet Google Cloud — Création de zéro (si le projet a disparu)

Si le projet Google Cloud existant (`poste-youtube-505016` ou autre) a été
supprimé ou est inaccessible, il faut en créer un nouveau :

1. Aller sur **console.cloud.google.com** — vérifier que tu es connecté
   avec le compte qui **possède la chaîne YouTube** (pas un autre compte)
2. Dans le sélecteur de projet (en haut à gauche), cliquer **NOUVEAU PROJET**
3. Nommer explicitement (ex. `dark-chronicles-youtube`)
4. Une fois créé, **sélectionner ce projet** dans le sélecteur

### Activer l'API + Configurer l'écran de consentement

1. Aller sur `console.cloud.google.com/apis/api/youtube.googleapis.com`
   → vérifier que le bon projet est sélectionné en haut → **ACTIVER**
2. Aller sur `console.cloud.google.com/apis/credentials/consent`
   → **Type : Externe** → remplir :
   - Nom de l'app : `Dark Chronicles Upload` (ou équivalent)
   - Email de support : l'email de la chaîne YouTube
   - Email du développeur : le même
3. Onglet **Scopes** (ou plus bas dans la page) → **Ajouter des scopes**
   → chercher `youtube.upload` → cocher → **Ajouter** → **Enregistrer**
   ⚠️ Ne pas passer cette étape — sans scope configuré, l'écran de
   consentement est incomplet et Google refuse l'auth.
4. Onglet **Utilisateurs test** → **+ Ajouter des utilisateurs**
   → entrer l'email de la chaîne YouTube
   → **Enregistrer**

### Créer le client OAuth

1. Aller sur `console.cloud.google.com/apis/credentials`
2. **+ Créer des identifiants** → **ID client OAuth**
3. Type d'application : **Application de bureau** (Desktop app)
   ⚠️ Si tu sélectionnes **Application Web** par erreur, Google demande
   des `origines JavaScript` et `URI de redirection` — et ça ne marche pas
   pour le flow desktop. Si c'est déjà fait, édite le client OAuth et
   ajoute `urn:ietf:wg:oauth:2.0:oob` dans URI de redirection autorisés.
4. Nom : au choix (ex. `Dark Chronicles Desktop`)
5. **Créer** → la boîte de dialogue affiche l'ID client et le client_secret
6. Cliquer **⬇ Télécharger JSON** pour sauvegarder le fichier
7. Copier ce fichier dans `/root/projets/youtube-automation/client_secret.json`

### ⚠️ PIÈGE — Plusieurs comptes Google dans la console

Si tu utilises plusieurs comptes Google (ex. `monsunrise`, `pierre.business53`),
**le projet que tu vois dans la console dépend du compte connecté en haut à
droite**. Un projet créé avec le compte A n'est pas visible sous le compte B.
Avant de commencer :

1. Vérifie en haut à droite de la console **quel compte est connecté**
2. Ce compte doit être celui qui **possède la chaîne YouTube**
3. Le projet doit être visible sous ce compte
4. Si tu changes de compte, recharge la console avec l'URL complète du projet

### ⚠️ PIÈGE — Projet qui n'existe plus

Si l'ancien projet (`poste-youtube-505016` ou similaire) a été supprimé :

1. `client_secret.json` pointe vers un projet mort → l'API n'est pas activée
   → le navigateur affiche « Service non disponible pour votre compte »
2. Solution : créer un nouveau projet (section ci-dessus) et remplacer
   le `client_secret.json`
3. Ne PAS essayer de réutiliser l'ancien `client_secret.json` — il pointe
   vers un projet qui n'existe plus

### ⚠️ ÉTAPE 0 — Identifier le bon compte Google

Le token OAuth est lié au compte Google qui **possède la chaîne YouTube**,
PAS au compte admin du projet Google Cloud. Si tu reçois un message
« **Service non disponible pour votre compte** » en ouvrant l'URL d'auth,
c'est que tu es connecté avec le mauvais compte.

1. Connecte-toi sur **youtube.com** dans ton navigateur — vérifie en haut à
   droite que c'est la chaîne que tu veux (icône + nom)
2. L'email lié à cette chaîne Google/YouTube est celui qu'il faut utiliser
   pour l'authentification OAuth
3. Ouvrir l'URL d'auth DANS UNE FENÊTRE DE NAVIGATION PRIVÉE si besoin,
   pour être sûr de pouvoir choisir le bon compte sans cookies résiduels

### Format client_secret.json

Le fichier téléchargé est au format standard :
```json
{"installed": {"client_id": "...", "project_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_secret": "...", "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]}}
```

## Flux d'échange manuel (deux process séparés) — PIÈGE PKCE

Le flow `InstalledAppFlow.authorization_url()` ajoute automatiquement PKCE
(`code_challenge` dans l'URL). Si l'URL est générée dans un process A et le
code échangé dans un process B, le `code_verifier` est perdu →
`invalid_grant: Missing code verifier`.

**Solution : générer l'URL SANS PKCE** et échanger avec le client_secret :

1. URL d'auth construite à la main :
```
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=CLIENT_ID&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fyoutube.upload&access_type=offline&prompt=consent
```
2. Utilisateur ouvre l'URL dans son navigateur, autorise, copie le code.
3. Échange UNE SEULE FOIS (le code est à usage unique — un second appel le
   consomme définitivement, même pour "vérifier") :
```python
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": code, "client_id": cid, "client_secret": csecret,
    "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
    "grant_type": "authorization_code"}, timeout=30)
```
4. Sauvegarder immédiatement le refresh_token dans le MÊME appel :
```python
creds = Credentials(token=data["access_token"],
    refresh_token=data["refresh_token"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=cid, client_secret=csecret,
    scopes=["https://www.googleapis.com/auth/youtube.upload"])
with open(token_path, "wb") as f: pickle.dump(creds, f)
```

## Erreurs à connaître

- `Service non disponible pour votre compte` → le compte Google connecté au
  navigateur pendant l'auth OAuth **n'est pas celui qui possède la chaîne
  YouTube** OU l'API YouTube Data v3 n'est pas activée sur le projet Google
  Cloud du `client_secret.json` utilisé. Vérification :
  1. La bonne chaîne YouTube est-elle connectée dans le navigateur ?
  2. L'API YouTube Data v3 est-elle activée sur le projet Google Cloud
     correspondant au `client_secret.json` ?
  3. L'email de la chaîne est-il dans les **Test users** de l'écran de
     consentement OAuth ?
  Solution : ouvrir l'URL d'auth en navigation privée pour choisir le bon
  compte, et/ou vérifier dans la console que le projet du client_secret
  a bien l'API activée.

- `invalid_grant: Token has been expired or revoked.` (RefreshError) →
  le refresh_token est mort (expiré ou révoqué). Symptôme typique : le
  pipeline génère la vidéo parfaitement (script → voix → clips → montage),
  mais l'upload échoue sur `next_chunk()` avec
  `google.auth.exceptions.RefreshError`. **Seule solution** : refaire le
  flux OAuth complet (supprimer le .pickle, vérifier le projet/API/test users
  dans la console, régénérer l'URL d'auth sans PKCE, ré-autoriser,
  ré-échanger le code). Voir section « Récupération après expiration ».

- `Service non disponible pour votre compte` + `Erreur 403: access_denied`
  simultanément → deux problèmes distincts : (1) le compte connecté n'est
  pas le bon, (2) l'email n'est pas dans les test users du projet.
  Ajouter l'email comme test user puis réessayer l'URL d'auth.

- `authenticatedUserAccountSuspended` (403) → le compte YouTube lié à
  l'email Google est suspendu. Changer de compte Google, pas de fix code.

- `insufficientPermissions` sur channels.list/videos.list/videos.delete →
  **normal** : le scope `youtube.upload` ne couvre QUE videos.insert +
  thumbnails.set. Ne pas tester avec channels.list.

- Miniatures custom : 403 `forbidden` sur chaîne récente (< 48h) même avec
  téléphone vérifié. Attendre.

- Vidéo test de 1s sans audio → YouTube abandonne le traitement
  ("processing abandoned"). Utiliser une vraie vidéo avec piste audio pour tester.

## Récupération après expiration du token (`invalid_grant`)

Quand le cron log montre `google.auth.exceptions.RefreshError: invalid_grant:
Token has been expired or revoked.`, suivre cette procédure :

### 1. Identifier le bon projet Google Cloud

Le `client_secret.json` existant pointe vers un projet précis (champ
`project_id`). **Ne pas en recréer un nouveau** — utiliser le projet
existant qui a déjà l'API activée et l'écran de consentement configuré.
Si tu changes de projet, l'API risque de ne pas être activée sur le
nouveau → « Service non disponible ».

### 2. Vérifier dans la console (avant de refaire l'auth)

1. Aller sur https://console.cloud.google.com/apis/api/youtube.googleapis.com
   → vérifier que le bon projet est sélectionné (même `project_id` que le
   `client_secret.json`) → « API activée »
2. Aller sur https://console.cloud.google.com/apis/credentials/consent
   → vérifier que l'email de la chaîne YouTube est dans **Test users**
3. Aller sur https://console.cloud.google.com/apis/credentials
   → si le client OAuth Desktop existe encore : bon. Sinon en recréer un
   (type: Application de bureau) et télécharger le JSON.

### 3. Supprimer l'ancien token

```bash
rm /root/projets/youtube-automation/output/youtube_token.pickle
```

### 4. Générer l'URL d'auth (sans PKCE)

```python
import json
with open("client_secret.json") as f:
    sec = json.load(f)["installed"]
cid = sec["client_id"]
redirect = sec["redirect_uris"][0]
scope = "https://www.googleapis.com/auth/youtube.upload"

url = (f"https://accounts.google.com/o/oauth2/auth"
       f"?response_type=code&client_id={cid}"
       f"&redirect_uri={redirect}&scope={scope}"
       f"&access_type=offline&prompt=consent")
print(url)
```

### 5. Ouvrir l'URL et autoriser

- De préférence en **navigation privée** (pas de cookies résiduels)
- Se connecter avec l'email **qui possède la chaîne YouTube**
- Choisir la chaîne si demandé
- Copier le code

### 6. Échanger le code (une seule fois !)

```python
import requests, json, pickle
from google.oauth2.credentials import Credentials

with open("client_secret.json") as f:
    sec = json.load(f)["installed"]
cid, csecret = sec["client_id"], sec["client_secret"]
redirect = sec["redirect_uris"][0]

code = input("Code > ")
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": code, "client_id": cid, "client_secret": csecret,
    "redirect_uri": redirect, "grant_type": "authorization_code"}, timeout=30)

if not resp.ok:
    print(f"ERREUR {resp.status_code}: {resp.text}")
    exit(1)

data = resp.json()
creds = Credentials(token=data["access_token"],
    refresh_token=data.get("refresh_token"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=cid, client_secret=csecret,
    scopes=["https://www.googleapis.com/auth/youtube.upload"])

with open("output/youtube_token.pickle", "wb") as f:
    pickle.dump(creds, f)
print("OK — token sauvegardé")
```

### 7. Vérifier

```bash
cd /root/projets/youtube-automation
python3 -c "
import pickle
with open('output/youtube_token.pickle','rb') as f:
    creds = pickle.load(f)
print(f'Token valide: {creds.valid}')
print(f'Expired: {creds.expired}')
print(f'Refresh token: {bool(creds.refresh_token)}')
```

## Upload resumable + publishAt (planification)

```python
media = MediaFileUpload(path, mimetype="video/mp4",
                        chunksize=5*1024*1024, resumable=True)
body = {"snippet": {"title":..., "description":..., "tags":[...],
                    "categoryId": "27", "defaultLanguage": "fr",
                    "defaultAudioLanguage": "fr"},
        "status": {"privacyStatus": "private",   # private OBLIGATOIRE pour publishAt
                   "selfDeclaredMadeForKids": False,
                   "publishAt": "2026-08-18T12:00:00+02:00"}}
request = youtube.videos().insert(part="snippet,status",
                                  body=body, media_body=media)
response = None
while response is None:
    status, response = request.next_chunk()   # status.progress() = 0-1
```

- publishAt = RFC 3339 avec offset local (`datetime.now().astimezone().isoformat(timespec="seconds")`)
- Si privacy ≠ private avec publishAt → forcer private
- Séries : uploader Partie 2 APRÈS Partie 1 pour inclure l'URL croisée dans la description

## Compte multi-chaînes

Un token OAuth est lié au compte Google, l'upload part sur la chaîne
sélectionnée au consentement. Pour une nouvelle chaîne brand : refaire
l'URL d'auth (sans PKCE) et choisir la bonne chaîne pendant le consentement,
puis ré-échanger le code.
