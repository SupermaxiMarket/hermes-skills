# Cloudflared trycloudflare DNS NXDOMAIN sur WSL

## Problème

Depuis WSL (Ubuntu), `curl https://<random>.trycloudflare.com` retourne
`curl: (6) Could not resolve host` même après que cloudflared a confirmé
le tunnel enregistré et que le site est parfaitement accessible depuis
l'extérieur (navigateur Windows, téléphone, autre machine).

## Cause

WSL utilise `systemd-resolved` qui écoute sur `127.0.0.53:53` (relayé
par `10.255.255.254`). Ce résolveur local retourne systématiquement
**NXDOMAIN** pour les sous-domaines trycloudflare fraîchement créés, même
quand les résolveurs globaux (Google 8.8.8.8, Cloudflare 1.1.1.1) les
connaissent déjà.

La séquence typique :
1. Cloudflare confirme `Registered tunnel connection` + crée le DNS
2. `dig @8.8.8.8 <sous-domaine>.trycloudflare.com +short` → `104.16.230.132`
3. `host <sous-domaine>.trycloudflare.com` (via le résolveur WSL) → `NXDOMAIN`

Le sous-domaine est visible mondialement mais pas depuis WSL.

## Solutions de contournement

### Depuis WSL : `--resolve`

```bash
curl --resolve '<hostname>:443:104.16.230.132' https://<hostname>/path
```

Où `104.16.230.132` (ou `104.16.231.132`) est une adresse anycast de
Cloudflare pour `trycloudflare.com`. Les deux IPs sont stables.

### Depuis Windows (recommandé)

Ouvrir l'URL directement dans le navigateur Windows (Chrome, Edge, Firefox)
— ça marche immédiatement. Le résolveur Windows (ou les résolveurs en aval)
voit le DNS correctement.

### Attendre

Parfois le résolveur WSL finit par voir le DNS après 2-5 minutes. Pas fiable.

## Dans le code de vérification (scripts/agents)

Quand un script doit vérifier qu'un tunnel est reachable depuis WSL,
utiliser `--resolve` au lieu de l'URL nue :

```python
import subprocess
# Au lieu de subprocess.run(["curl", "-s", url])
subprocess.run([
    "curl", "-s", "--max-time", "15",
    "--resolve", f"{hostname}:443:104.16.230.132",
    url
])
```

Ou bien, laisser tomber la vérification WSL et informer l'utilisateur que
l'URL est accessible depuis son navigateur Windows.
