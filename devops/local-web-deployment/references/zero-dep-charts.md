# Graphiques zéro dépendance (CSS pur)

Quand Chart.js est bloqué par un adblocker, en navigation privée, ou
quand le réseau est lent, `initCharts()` plante → `updateRecommendations()`
n'est jamais appelée → l'app s'affiche vide (Mayweather écran blanc).

## Découplage d'init (minimum vital)

```js
// Charts isolés — ne bloquent JAMAIS le reste de l'init :
try { initCharts(); updateCharts(); } catch (e) {
  console.warn('Chart.js non chargé');
  // fallback HTML optionnel
}
updateRecommendations(); // TOUJOURS exécuté, indépendant des charts
```

## Dual-CDN (filet de sécurité intermédiaire)

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.4/chart.umd.min.js"></script>
<script>window.Chart || document.write('<scr'+'ipt src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"><\/scr'+'ipt>');</script>
```

## Zéro dépendance externe (recommandé)

Pour tout outil HTML standalone, remplacer Chart.js par des graphiques
purement CSS :

### Camembert/Doughnut — `conic-gradient()`

```js
var total = items.reduce(function(s, i) { return s + i.v; }, 0);
var offset = 0;
var segments = items.map(function(item, i) {
  var pct = item.v / total * 100;
  var seg = PALETTE[i % PALETTE.length] + ' ' + offset + '% ' + (offset + pct) + '%';
  offset += pct;
  return seg;
});
el.style.background = 'conic-gradient(' + segments.join(', ') + ')';
// Légende : liste HTML avec swatch + nom + montant
```

Propriétés CSS :
- Largeur/hauteur fixes (ex. 140px), `border-radius: 50%`
- Texte centré au milieu (nombre de postes ou total)
- 12 couleurs de la palette, avec "… +X autres" si dépassement

### Barres comparatives — flexbox

```js
var maxVal = Math.max.apply(null, data.map(function(i) {
  return Math.max(i.b, i.a);
}));
// Chaque ligne :
var wB = Math.max(2, item.b / maxVal * 100); // budget
var wA = Math.max(2, item.a / maxVal * 100); // réel
// Deux .bar-track côte à côte, fill .bar-fill.blue / .bar-fill.red
```

Structure HTML :
```html
<div class="bar-row">
  <span class="bar-label">Catégorie</span>
  <div class="bar-track"><div class="bar-fill blue" style="width:60%"></div></div>
  <div class="bar-track"><div class="bar-fill red" style="width:80%"></div></div>
  <span class="bar-val">1 500 CHF</span>
</div>
```

CSS :
```css
.bar-row { display:flex; align-items:center; gap:6px; margin-bottom:3px; font-size:.68rem; }
.bar-label { width:100px; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex-shrink:0; color:#6b7280; }
.bar-track { flex:1; height:14px; background:#e5e7eb; border-radius:3px; overflow:hidden; }
.bar-fill { height:100%; border-radius:3px; transition:width .3s; }
.bar-fill.blue { background:#3b82f6; }
.bar-fill.red { background:#ef4444; }
```

## Avantages du zéro dépendance

- Zéro requête réseau — pas de CDN à bloquer
- Même rendu dans tous les navigateurs (pas de version JS qui change)
- Fonctionne en navigation privée, avec uBlock Origin, Tor, hors ligne
- 2-3 KB de CSS/JS au lieu de 200+ KB pour Chart.js
- Pas de try/catch nécessaire — le rendu est synchrone dans le DOM