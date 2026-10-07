# Remotion — Programmatic Video Creation

## Overview

Remotion is a Node.js library that creates MP4 videos programmatically using React components. Each frame is rendered via Chromium. Useful when the user asks for animated explainers, promo videos, data-driven motion graphics, or automated social media content.

**Not a replacement for** the Dark Chronicles pipeline (narration + Pexels clips + ffmpeg). Remotion excels at motion graphics, text animations, and code-driven video — not documentary-style content.

## System Requirements (Pierre's WSL)

| Requirement | Status |
|-------------|--------|
| Node.js v18+ | ✅ v22.22.2 |
| npm | ✅ 10.9.7 |
| Chromium (rendering) | ✅ /usr/bin/chromium-browser |
| ffmpeg | ✅ installed |
| RAM | ✅ 15GB (13GB free) |
| Disk | ✅ 902GB free |

## License

- **Free**: individuals and for-profit ≤3 employees
- **Company license**: required for larger organizations
- Pierre qualifies as individual → free license

## When to Use

- Animated explainer / promo videos (Vaulty, Budget Familial, etc.)
- Automated Daily AI Brief video version (headlines → animated Short)
- Data visualization videos (charts, graphs building up)
- Intro/outro signatures for any video project
- Social media ads with motion design

## When NOT to Use

- Dark Chronicles / true crime narration + clips (ffmpeg is faster and better)
- Live-action or screen recording content
- Quick-and-dirty assembly of stock clips + voiceover (use existing pipeline)

## Quick Start

```bash
# Scaffold a new project
npx create-video@latest --yes --blank --no-tailwind my-video
cd my-video
npm i

# Start Studio preview
npx remotion studio --no-open

# Render final video
npx remotion render
```

## AI Agent Integration

Remotion provides pre-built skills for AI agents (Claude, Codex, Hermes) in their repo under `.agents/skills/` and `packages/skills/skills/`:
- `remotion-best-practices` — router for all Remotion skills
- `remotion-create` — scaffold a new project and composition
- `remotion-render` — rendering options (CLI, Lambda, SSR)
- `remotion-docs` — Algolia search + .md page fetching
- `remotion-studio` — launch and configure Studio
- `remotion-saas` — building SaaS apps with `<Player>`

The skills are at: https://github.com/remotion-dev/remotion/tree/main/packages/skills/skills

## Key Docs

- https://www.remotion.dev/docs/ — full documentation
- Append `.md` to any docs URL for raw markdown source

## Rendering

```bash
# Video
npx remotion render <composition-id> --output out/video.mp4

# Still image
npx remotion still <composition-id> --output out/still.png
```

For Lambda / server-side rendering, see `remotion-saas` skill references.

## Pitfalls

- Rendering is **frame-by-frame** — slower than ffmpeg for simple concatenation but necessary for precise animations
- Requires Chromium — ensure it's in PATH (on WSL: `/usr/bin/chromium-browser`)
- License is NOT fully open-source — the free tier covers individuals but check before commercial redistribution of the tool itself
- The `create-video` scaffolder rejects non-empty directories — scaffold into a subfolder or clean the target first
