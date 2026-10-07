# Access gate — remplacer 401 par redirection 302 vers /login

## Problème

L'access gate de Hermes3D (`server/access-gate.js`) renvoie une page blanche avec le message :

```
Studio access token required. Set the studio_access cookie to access this page.
```

L'utilisateur voit ça en arrivant sur `/office` (ou toute page protégée) et ne sait pas qu'il doit aller sur `/login`. Il n'y a AUCUN lien, aucune indication. Résultat : frustration légitime (« c'est quoi ce bordel »).

## Fix

Dans `server/access-gate.js`, fonction `handleHttp`, remplacer le bloc `else` (non-API) :

### Avant

```javascript
} else {
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "text/plain");
  res.end(
    auth.limited
      ? "Too many failed studio access attempts. Wait a minute and retry."
      : "Studio access token required. Set the studio_access cookie to access this page."
  );
}
```

### Après

```javascript
} else {
  // Redirect to login page instead of showing a raw error
  res.statusCode = 302;
  res.setHeader("Location", "/login");
  res.end();
}
```

## Résultat

1. L'utilisateur arrive sur `http://host:3000/` → Next.js redirige vers `/office`
2. L'access gate voit pas de cookie → 302 vers `/login`
3. Le navigateur suit la redirection → page de login avec formulaire
4. L'utilisateur entre le token OU clique le lien direct `?token=...`
5. Cookie posé, redirigé vers `/office`, accès OK

## Note

Les endpoints `/api/*` continuent de recevoir une 401 JSON — c'est voulu (appels programmatiques). Seules les pages HTML (non-API) sont redirigées.