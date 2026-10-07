# HTML statique — pièges cross-navigateurs

Ce document rassemble les correctifs appliqués lors du rebuild du site
Budget Retraité Suisse (HTML/CSS/JS pur, pas de framework) pour que
l'affichage et le comportement soient identiques sur Chrome, Firefox,
Safari (desktop + iOS), Edge et Brave.

## Inputs numériques — remplacer `type="number"`

Le `type="number"` avec `step="0.01"` pose trois problèmes :

1. **Safari** ignore `step` pour les décimales si le navigateur attend
   un point comme séparateur alors que la locale utilise une virgule.
2. **Firefox mobile** affiche un clavier sans virgule dans certains cas.
3. **Chrome** accepte les virgules mais les ignore silencieusement, ce qui
   produit `NaN` après `parseFloat` sans prétraitement.
4. **Step validation** — Chrome bloque `0.01` si on tape `0.001`,
   Firefox accepte, Safari accepte mais arrondit différemment.

**Solution :** `type="text"` + `inputmode="decimal"` + traitement manuel :

```js
function toNum(v) {
  const n = parseFloat(String(v).replace(/,/g, '.').replace(/[^0-9.\-]/g, ''));
  return isFinite(n) ? n : 0;
}
```

- `inputmode="decimal"` → clavier numérique avec virgule sur mobile.
- `onfocus="this.select()"` → sélectionne tout au focus (comportement natif
  de `type="number"` que `text` n'a pas).
- Jamais `type="number"` pour des montants en CHF avec décimales.

## Stockage local — `localStorage` en navigation privée

- **Safari (iOS/desktop)** et **Firefox** en mode navigation privée lancent
  une `SecurityError` ou `QuotaExceededError` à la première écriture.
- **Chrome incognito** autorise localStorage mais l'isole par session.

**Solution :** wrapper try/catch systématique :

```js
function storageAvailable() {
  try { const k = '_test_'; localStorage.setItem(k, '1'); localStorage.removeItem(k); return true; }
  catch (e) { return false; }
}
```

- `loadData()` et `saveData()` doivent être enveloppés dans des try/catch
  et retomber gracieusement sur les données par défaut.
- Afficher un indicateur visuel quand le stockage est indisponible.

## Troncature multi-byte

`String.prototype.substring(start, end)` coupe sur des unités de code
UTF-16, pas sur des caractères. Un emoji (2 unités) ou un caractère
accentué (é, ü — 1 unité mais longueur visuelle 1) peut être coupé à
moitié, produisant un caractère invalide.

**Solution :** utiliser `String.slice()` + recherche du dernier espace :

```js
function trunc(str, len) {
  if (!str || str.length <= len) return str || '';
  let s = str.slice(0, len);
  const last = s.lastIndexOf(' ');
  if (last > len * 0.5) s = s.slice(0, last);
  return s + '…';
}
```

## Échappement HTML — ne pas oublier les single quotes

Beaucoup de fonctions d'échappement maison couvrent `& < > "` mais pas `'`.
Or les single quotes cassent la concaténation innerHTML quand la propriété
est utilisée dans un attribut entre quotes :

```js
function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
    .replace(/\//g, '&#x2F;');
}
```

## Chart.js — version pin

Le CDN générique `https://cdn.jsdelivr.net/npm/chart.js` résout vers la
dernière version, qui peut changer entre deux chargements de page. Les API
diffèrent entre v3 et v4 (constructeur, options, registre de plugins).

**Solution :** épingler une version UMD majeure :
```
https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js
```

- v4 utilise `new Chart(ctx, config)` (inchangé depuis v3) mais les plugins
  doivent être enregistrés avec `Chart.register()`.
- `responsive: true` + `maintainAspectRatio: false` + CSS `height: 300px`
  sur le conteneur + `width:100% !important; height:100% !important` sur
  le canvas → même hauteur sur tous les moteurs de rendu.

## Impression — `color-adjust`

La règle `-webkit-print-color-adjust: exact` est nécessaire pour conserver
les couleurs de fond à l'impression sur Chrome/Safari, mais Firefox et les
navigateurs récents utilisent la propriété standard.

**Solution :** les trois avec fallback :
```css
@media print {
  body { -webkit-print-color-adjust: exact; color-adjust: exact; print-color-adjust: exact; }
}
```

## Tableaux responsives — défilement horizontal

Les tableaux avec beaucoup de colonnes (budget, 5+ colonnes) cassent
le layout sur mobile.

**Solution :** wrapper avec overflow + touch scroll :
```css
.tbl-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { min-width: 640px; border-collapse: collapse; }
```

- Safari iOS sans `-webkit-overflow-scrolling: touch` a un scroll à
  inertie désagréable.
- `min-width` garantit que les colonnes ne s'écrasent pas sur petit écran.

## Animations — préférer `@keyframes` aux transitions seules

Les transitions CSS sur `opacity` + `transform` ne sont pas fiables sur
Safari quand l'élément est ajouté dynamiquement au DOM.

**Solution :** animation nommée avec `animation-fill-mode` :
```css
@keyframes fadeSlideIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeSlideIn 0.25s ease-out; }
```

## Serveur local — Python `http.server`

Pour un HTML statique, pas besoin de Node. Tout Python récent a un serveur
HTTP natif :

```bash
cd ~/projets/mon-app && python3 -m http.server 8760
```

- Port libre au-delà de 8000 pour éviter les conflits avec les autres apps.
- Compatible tunnel cloudflared : `cloudflared tunnel --url http://127.0.0.1:8760`
- Pas de hot-reload (forcément — c'est du statique). Modifier → recharger.