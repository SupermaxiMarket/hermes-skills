#!/usr/bin/env python3
"""
Ré-authentification YouTube OAuth (sans PKCE) — pour récupérer d'un
`invalid_grant: Token has been expired or revoked.

Usage:
    python3 reauth_youtube.py

Étapes :
    1. Lit client_secret.json
    2. Supprime l'ancien youtube_token.pickle
    3. Affiche l'URL d'auth (sans PKCE)
    4. Prend le code en entrée
    5. Échange le code contre token + refresh_token
    6. Sauvegarde le pickle
"""
import json, os, pickle, sys
import requests
from google.oauth2.credentials import Credentials

BASE = os.path.dirname(os.path.abspath(__file__))
SECRET_PATH = os.path.join(BASE, "client_secret.json")
TOKEN_PATH = os.path.join(BASE, "output", "youtube_token.pickle")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

if not os.path.exists(SECRET_PATH):
    print(f"❌ client_secret.json introuvable → {SECRET_PATH}")
    sys.exit(1)

with open(SECRET_PATH) as f:
    secret = json.load(f)["installed"]
cid = secret["client_id"]
csecret = secret["client_secret"]
redirect = secret["redirect_uris"][0]

# Supprimer ancien token
if os.path.exists(TOKEN_PATH):
    os.remove(TOKEN_PATH)
    print("   🗑️  Ancien token supprimé")

# URL sans PKCE
auth_url = (
    "https://accounts.google.com/o/oauth2/auth"
    f"?response_type=code&client_id={cid}"
    f"&redirect_uri={redirect}"
    f"&scope={SCOPES[0]}"
    "&access_type=offline&prompt=consent"
)

print("\n" + "="*60)
print("🔐  AUTHENTIFICATION YOUTUBE")
print("="*60)
print()
print("1. Ouvre ce lien (en navigation privée de préférence) :")
print(f"\n   {auth_url}\n")
print("2. Connecte-toi avec le compte qui POSSÈDE la chaîne YouTube")
print("3. Choisis la bonne chaîne si demandé")
print("4. Autorise (scope youtube.upload)")
print("5. COPIE le code d'autorisation et colle-le ci-dessous")
print()
code = input("   Code d'auth > ").strip()

print("\n   ↻ Échange du code...")
resp = requests.post("https://oauth2.googleapis.com/token", data={
    "code": code,
    "client_id": cid,
    "client_secret": csecret,
    "redirect_uri": redirect,
    "grant_type": "authorization_code",
}, timeout=30)

if not resp.ok:
    print(f"\n   ❌ ERREUR {resp.status_code}")
    print(f"   {resp.text}")
    sys.exit(1)

data = resp.json()
if not data.get("refresh_token"):
    print("   ⚠️  Pas de refresh_token — revérifie access_type=offline dans l'URL")

creds = Credentials(
    token=data["access_token"],
    refresh_token=data.get("refresh_token"),
    token_uri="https://oauth2.googleapis.com/token",
    client_id=cid,
    client_secret=csecret,
    scopes=SCOPES,
)

os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
with open(TOKEN_PATH, "wb") as f:
    pickle.dump(creds, f)

print(f"   ✓ Token sauvegardé → {TOKEN_PATH}")
print(f"   ✓ Refresh token présent: {bool(creds.refresh_token)}")
print("\n✅  AUTH OK — Tu peux uploader !")