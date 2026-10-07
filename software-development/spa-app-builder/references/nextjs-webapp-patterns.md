# Next.js multi-page web app — project patterns

Used when `spa-app-builder`'s static SPA approach won't fit:
10+ routes, server-rendered pages, real framework stack (Next.js + React + Tailwind).

## Stack choices (proven on this WSL box)

| Component | Choice | Reason |
|-----------|--------|--------|
| Framework | Next.js 16 (App Router) | Page-per-directory routing, Turbopack build |
| UI | React 19 + TypeScript | JSX components, type safety |
| CSS | Tailwind v4 via `@import` | No tailwind.config.ts needed; uses PostCSS plugin |
| Fonts | Geist (via next/font/google) | Bundled with create-next-app |
| PWA | `manifest.json` + meta tags | standalone display, theme-color |

## Tailwind v4 in Next.js 16

Tailwind v4 uses a PostCSS-only approach. There is NO `tailwind.config.ts`.

**postcss.config.mjs:**
```js
const config = {
  plugins: {
    "@tailwindcss/postcss": {},
  },
};
export default config;
```

**globals.css (imports Tailwind AND defines theme):**
```css
@import "tailwindcss";

:root {
  --blue: #2563EB;
  --off-white: #F8FAFC;
  --night: #172554;
}

@theme inline {
  --color-blue: var(--blue);
  --color-off-white: var(--off-white);
  --color-night: var(--night);
}

/* Custom utility classes */
.lifebox-card {
  border-radius: 1rem;
  transition: all 0.25s ease;
}
.lifebox-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px -8px rgba(0,0,0,0.15);
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-up { animation: fadeUp 0.5s ease-out both; }
```

Note: class-based colors only work for static known values. For dynamic colors
(passing a hex value from data), use inline `style={{ backgroundColor: `${color}20` }}`
rather than trying to compute a Tailwind class name dynamically.

## App Router: one directory = one route

```
app/
├── page.tsx               # /
├── layout.tsx             # Root layout (all pages)
├── globals.css            # Imports Tailwind + custom styles
├── dashboard/page.tsx     # /dashboard
├── chat/page.tsx          # /chat
├── auth/login/page.tsx    # /auth/login
├── documents/page.tsx     # /documents
└── documents/[id]/page.tsx # /documents/:id  (dynamic route)
```

**Dynamic route pattern** (Next.js 16):
```tsx
export default function Page({ params }: { params: { id: string } }) {
  const doc = demoDocuments.find((d) => d.id === params.id) || fallback;
  // ...
}
```

**Root layout** re-exports `Geist`/`Geist_Mono` fonts and sets `lang="fr"`:
```tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "App Name",
  description: "...",
  manifest: "/manifest.json",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="fr" className={`${geistSans.variable} ... h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
```

## Building a large project (20+ pages) in one session

Order matters to avoid rework and keep the context window manageable:

### Phase 1: Infrastructure
1. **Types & interfaces** (`lib/types.ts`) — every domain type, enum, and interface upfront.
   This governs all downstream code. Get the enums right (DocumentStatus, RiskLevel).
2. **Demo data** (`lib/demo-data.ts`) — populate realistic examples that exercise all types.
   Mark examples with `isExample: true` so the UI can flag them.
3. **Translations** (`lib/translations.ts`) — one file with the full tree, French default.
   Structure it so adding DE/IT/EN only requires a new object, not a refactor.
4. **Business logic** (ai-assistant.ts, auth.ts, store.ts) — simulation layer that mirrors the
   real API interface, so swapping in a real backend later only touches the lib files.

### Phase 2: Layout & styling
Write `globals.css` and `app/layout.tsx` once. These touch every page so get them right
before any pages. Set `@theme` colors, custom utility classes (card hover, animation), and
the Geist font config together.

### Phase 3: Pages in dependency order
1. **Public pages** first (home, auth, info pages) — they have no private header dependency.
2. **Shared private header** — define it ONCE as a local function in the first private page,
   then reuse the same pattern in all private pages. Export it if multiple files import it.
3. **Remaining private pages** — batch them by screen type (documents list + document detail,
   tasks + reminders, family + local-guide + create, settings as the last private page).

### Phase 4: Build-verify between phases
```bash
npx next build   # ~6 seconds after initial warp
```
Catches TypeScript errors, missing imports, and broken routes before the next phase.
The build also confirms every route compiles — a successful build with all expected routes
is your final validation before exposing the app.

### Pitfalls

- **Do NOT write pages in alphabetical order** — write them in dependency order
  (public → shared header → private with header → dependent detail). The private header
  pattern (back arrow + title + nav) belongs in every private page and should be defined
  in the first page that needs it, then reused in all others via export.
- **Tailwind v4 does NOT use `@tailwind` directives** — no `@tailwind base;` in CSS.
  Use `@import "tailwindcss"` instead. The PostCSS plugin handles everything.
- **No `tailwind.config.ts`** — in v4, the PostCSS plugin replaces the config file.
  Custom theme values go in `globals.css` as CSS custom properties + `@theme inline`.
- **`style={{}}` for dynamic colors** — Tailwind classes like `bg-[#2563EB]` only work
  for literal values in the source. When the color comes from data (card.color),
  use inline `style={{ backgroundColor: `${card.color}` }}`.
- **Public page headers are different from private ones** — public headers have
  logo + nav links; private headers have back-arrow + title + user nav. Define them
  separately, don't try to unify them with conditional logic.
- **Empty state for every collection** — every list page needs an EmptyState component
  (icon, title, description) shown when the data array is empty. Otherwise the user sees
  a blank page with no explanation.
- **Build verification before tunnel** — always run `npx next build` before starting
  cloudflared. A failed build means a broken tunnel.
- **Function component rendering JSX directly** — when defining helper functions that
  return JSX inside a page.tsx, use the pattern `function MyHelper({ children }: { children: React.ReactNode })`
  and explicitly `import React from "react"` if the linter complains.