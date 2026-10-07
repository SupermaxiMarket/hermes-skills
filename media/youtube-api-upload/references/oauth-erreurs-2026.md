# Erreurs OAuth YouTube (2026) — Diagnostics

## "Service non disponible / Accès bloqué : la demande de cette appli n'est pas valide"

**Cause** : Utilisation du flux OOB (`urn:ietf:wg:oauth:2.0:oob`) qui est
déprécié. Google n'accepte plus ce redirect.

**Fix** : Créer un client **Application Web** avec redirect URI
`http://127.0.0.1:8080` et serveur HTTP local.

## "Accès bloqué : la demande de cette appli n'est pas valide / Erreur 400: redirect_uri_mismatch"

**Cause** : L'URI de redirection dans l'URL d'auth ne correspond pas à ceux
enregistrés dans la Console Google.

**Fix** : Vérifier que `redirect_uri` dans l'URL d'auth matche **exactement**
ce qui est dans le client OAuth. Propagation Google : 5 min → quelques heures.

## "Vous avez tenté d'accéder à un service non disponible pour votre compte"

**Cause** : L'écran de consentement OAuth n'a pas l'email en test users.

**Fix** : Console → Écran de consentement → Test users → ajouter
l'email du compte YouTube (pierre.business53@gmail.com).

## "Domaine non valide : le domaine ne peut pas contenir d'espace blanc"

**Cause** : L'URL page d'accueil contient un `@` ou espace.
Ex: `https://www.youtube.com/@DarkChronicles-x1r`

**Fix** : Utiliser une URL sans `@` : `https://www.youtube.com/`

## "Domaine non valide : l'URI ne doit pas inclure de schéma (http:// ou https://)"

**Cause** : Dans le champ "Domaines autorisés", mettre une URL complète au
lieu du domaine nu.

**Fix** : Mettre juste `youtube.com` (sans https://, sans www).

## HTTP 401 après mise à jour du token

**Cause** : Le nouveau token GitHub n'a pas encore été autorisé sur les repos,
ou le scope `read:org` est manquant.

**Fix** : `gh auth login --with-token < nouveau_token >` ou dans les settings
GitHub → token → ajouter les scopes/repos.

## 403 Thumbnail — "authenticated user doesn't have permissions"

**Cause** : Le compte YouTube n'a pas le badge vérification de chaîne.

**Fix** : Uploader les miniatures manuellement via YouTube Studio, ou activer
la vérification de chaîne (nécessite 100 abonnés + téléphone).

## invalid_grant: Token has been expired or revoked

**Cause** : Le token OAuth YouTube (dans le pickle) a expiré et n'a pas de
refresh_token, ou le refresh_token lui-même est révoqué.

**Fix** : Supprimer le pickle et refaire l'auth complète (section Flow OAuth).