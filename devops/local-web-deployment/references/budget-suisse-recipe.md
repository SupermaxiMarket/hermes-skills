# Budget Suisse — static HTML deployment recipe

## Context

Single-page HTML budget tracker for a retired couple, served statically
via Python http.server and tunneled through cloudflared, or served via
Hermes3D's Next.js `public/` directory at `/budget/`.

## Data pre-population

The app must open with the user's REAL financial figures, not defaults:

- Revenue: 3 sources (AVS 3652, LPP 1080, Hoirie 70) → total 4802 CHF
- Budget: 26 categories, planned total 5177.50 CHF, actual total 7092.13 CHF
- Balance: -2290.13 CHF

These must be embedded in TWO places in the HTML:
1. The default array declarations (`let revenueData = [...]`, `let budgetData = [...]`)
2. The reset function in `resetAll()` — same arrays, not old defaults

If they diverge, clicking "Réinitialiser" restores wrong numbers.

## Deployment via Hermes3D public/ (stable, alongside 3D office)

```bash
mkdir -p ~/projets/hermes-3d/public/budget
cp ~/projets/budget-suisse/index.html ~/projets/hermes-3d/public/budget/
```

Then accessible at `https://<hermes3d-url>/budget/index.html` — no extra
tunnel needed. The access gate must be patched to allow `/budget` through
(see references/access-gate-static-bypass.md).

## Deployment via standalone server

```bash
cd ~/projets/budget-suisse && python3 -m http.server 8760 &
cloudflared tunnel --url http://127.0.0.1:8760
```

## Cross-browser gotchas

See references/cross-browser-html.md for the full list. Specific ones that
hit this project:

- `type="number"` with `step="0.01"` breaks differently on every browser
  → use `type="text"` + `inputmode="decimal"` + custom `toNum()` parser.
- `localStorage` throws in Safari/Firefox private browsing → wrap in try/catch
  with `storageAvailable()` check and fallback to defaults.
- `escapeHtml` must cover single quotes (`'` → `&#39;`) or innerHTML breaks
  when a category name like "Vêtements, coiffeur, esthétique" appears.
- Chart.js unpinned CDN changes between v3/v4 → pin to `chart.js@4.4.4/dist/chart.umd.min.js`.

## Data flow

1. `DOMContentLoaded` → `loadData()` (checks localStorage, falls back to defaults)
2. Everything renders from the in-memory arrays
3. Any change → `updateAll()` → `saveData()` (writes to localStorage)
4. Next load re-reads localStorage; defaults survive if storage is wiped