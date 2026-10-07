# trycloudflare DNS — divergence WSL vs global

Les quick tunnels trycloudflare génèrent un sous-domaine
`<random>.trycloudflare.com` qui peut prendre 30–60 secondes à
propager sur le DNS global, mais le résolveur DNS de WSL
(10.255.255.254) peut rester en NXDOMAIN indéfiniment même
quand Google DNS (8.8.8.8) ou Cloudflare (1.1.1.1) résolvent
déjà l'adresse.

## Symptômes

```
curl -v https://<random>.trycloudflare.com/login
→ "Could not resolve host: ... NXDOMAIN"

nslookup <random>.trycloudflare.com  → NXDOMAIN (résolveur local)
dig @8.8.8.8 <random>.trycloudflare.com → 104.16.230.132 (OK)
```

Mais depuis l'extérieur (navigateur Windows, téléphone), le site
est accessible.

## Vérification fiable depuis WSL

Utiliser `--resolve` pour contourner le DNS local :

```bash
curl -s --resolve '<host>:443:104.16.230.132' https://<host>/path
```

Les IP des edge Cloudflare sont stables : 104.16.230.132 et 104.16.231.132
(les mêmes que trycloudflare.com lui-même).

## Le DNS global finit par résoudre

Après 30–60 secondes, Google DNS et Cloudflare DNS retournent les IP.
Le problème est uniquement le résolveur local WSL (systemd-resolved
via 10.255.255.254) qui refuse les sous-domaines trycloudflare.

## Impact

- Le tunnel est fonctionnel et le trafic passe
- La vérification depuis WSL avec `curl` direct échoue (NXDOMAIN)
- La vérification par `--resolve` ou depuis un navigateur Windows passe
- Le service systemd tourne, mais les tests automatisés depuis WSL
  doivent utiliser `--resolve` pour confirmer la reachabilité