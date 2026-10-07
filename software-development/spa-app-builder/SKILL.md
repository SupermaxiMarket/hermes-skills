---
name: spa-app-builder
description: "Build SPAs with i18n, freemium, and tunnel deploy."
version: 1.0.0
author: hermes-curator
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web-app, spa, fullstack, static, deployment, i18n, freemium]
    related_skills: [popular-web-designs, claude-design, local-web-deployment]
---

# SPA App Builder

Build a complete functional single-page application from concept to public URL
in a single session. Covers the gap between "design a prototype" (claude-design)
and "deploy a static site" (local-web-deployment) — architecture, data model,
i18n, freemium, and build workflow for apps that *work*.

## When to Use

- User says "build the app", "make it work", "I need to use this"
- User asks for persistence, auth simulation, or monetization
- Deliverable is a working tool, not a design mockup
- Combine with `popular-web-designs` for visuals and `local-web-deployment` for serving

Do NOT use when the user wants a *design concept* — use `claude-design`.
Do NOT use when the app needs a real backend — localStorage is for zero-backend only.

## Scope: static SPAs only

This skill covers **static JS/HTML SPAs**: one HTML file, CSS show/hide routing, localStorage persistence, no framework.
It does NOT cover framework-based multi-page apps (Next.js, React, Express+SSR).

**Choose the right approach:**

| Need | Use this skill | Use a framework (Next.js/Express) |
|------|----------------|-----------------------------------|
| Routes (pages) | 1–5, toggled via CSS | 5+ with dedicated URLs & linking |
| State | localStorage only | Persistent DB or server sessions |
| Auth | Simulated (JS gate) | Real auth (JWT, session, OAuth) |
| Build tooling | None needed | TypeScript compiler, server runtime |
| Deploy | Any static host | Node.js host (Vercel, Railway, self) |
| Team scale | Solo prototype | Multi-page product |

When the user asks for 10+ pages, persistent document storage, multi-user,
or a structured application with real URLs — use Next.js or a comparable framework.
See `references/nextjs-webapp-patterns.md` for the proven workflow.
This skill stays the right choice for zero-framework interactive prototypes.

## Standard File Layout

```
/index.html       — HTML shell: landing + auth + app + modals
/styles.css       — Design system via CSS custom properties
/app.js           — All logic: data, routing, rendering
/i18n.js          — Translations (5 languages), loaded before app.js
```

## Architecture Rules

### Routing
CSS show/hide. No router.
```css
.page { display: none; }
.page.active { display: block; }
```

### State Management
Single global `data` object, JSON-serialized to `localStorage`:
```js
const STORAGE_KEY = 'app_data';
function loadData() { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || getDefaultData(); }
function saveData() { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
```

### Data Model
`getDefaultData()` returns the complete schema. Merge on load:
```js
function getDefaultData() {
  return { user: { name: '', plan: 'free' }, items: [], settings: { language: 'fr' } };
}
function loadData() {
  const raw = localStorage.getItem(STORAGE_KEY);
  const d = raw ? JSON.parse(raw) : {};
  const def = getDefaultData();
  for (const k in def) { if (!(k in d)) d[k] = JSON.parse(JSON.stringify(def[k])); }
  return d;
}
```

## i18n Pattern (5 languages)

Separate translation file:
```js
const I18N = {
  fr: { dashboard: "Tableau de bord", add: "Ajouter", ... },
  en: { dashboard: "Dashboard", add: "Add", ... },
  de: { dashboard: "Dashboard", add: "Hinzufügen", ... },
  it: { dashboard: "Cruscotto", add: "Aggiungi", ... },
  es: { dashboard: "Panel", add: "Añadir", ... },
};
function t(key) {
  const lang = (data?.settings?.language || 'fr');
  return I18N[lang]?.[key] || I18N['fr'][key] || key;
}
```

HTML uses `data-i18n="key"` attributes. Call `applyTranslations()` after every render. Keep keys flat.

## Freemium Pattern

| Feature | Free | Premium |
|---|------|---------|
| Documents | 5 | ∞ |
| Warranties | 3 | ∞ |
| Subscriptions | 3 | ∞ |
| Languages | 1 | 5 |

```js
const LIMITS = { documents: 5, warranties: 3, subscriptions: 3 };

function showAddModal(type) {
  const isPremium = data.user.plan === 'premium';
  const count = data[type + 's'].length;
  const limit = LIMITS[type + 's'];
  if (!isPremium && count >= limit) { showUpgradeModal(); return; }
}
```

Upgrade: sets `data.user.plan = 'premium'`, saves, re-renders, fires confetti.
Upgrade banner appears in-page at ~60% free capacity.

## Making it Work: prototype vs app

| Aspect | Prototype (claude-design) | App (this skill) |
|---|----|---|
| State | hardcoded in HTML | localStorage persistence |
| Data | static example array | CRUD add/delete |
| Limits | none | freemium enforced at modal entry |
| Language | one hardcoded | 5-language switcher |
| Landing+app | separate files | same HTML, section toggle |

## Verification Checklist

- [ ] Default data loads on first visit (no localStorage yet)
- [ ] Each page: add → list → persists after refresh → delete
- [ ] Stats/counters update after every add/delete
- [ ] Language switching updates ALL text (modals, placeholders, buttons)
- [ ] Free limit blocks past threshold (shows upgrade modal, does not overflow)
- [ ] Upgrade flow: sets premium, shows confetti, removes all limits
- [ ] Upgrade banner appears at ~60% free plan
- [ ] Settings: theme toggle, language highlights current
- [ ] All assets load: check browser console for 404s
- [ ] Mobile: sidebar collapses, pages reflow
- [ ] No console errors on any page

## Pitfalls

- **inline styles break pseudo-elements**: `::before`/`::after` don't work inline.
  Use class-based CSS for toggles and sliders.
- **LocalStorage schema drift**: always merge with defaults on load.
- **JS load order**: `i18n.js` must load BEFORE `app.js`.
- **data-i18n on dynamic content**: call `applyTranslations()` after every render.
- **Cloudflared URL changes each restart**: warn the user, or set up a named tunnel.