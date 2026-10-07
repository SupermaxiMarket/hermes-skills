---
name: remotion-video
description: "Use for animated videos, promos, or motion graphics."
version: 1.0.0
author: Hermes Agent
tags: [remotion, video, animation, react, motion-design]
---

# Remotion — Vidéos programmatiques

Transformer du code React en vidéos MP4 avec animations précises.

## Prérequis système (vérifier avant toute action)

```bash
node --version        # Requis: v18+
npm --version
chromium-browser --version || which chromium  # Chromium nécessaire au rendu
ffmpeg --version      # Optionnel, pour transcodage
```

⚠️ Sur WSL, Chromium est dans `/snap/bin/chromium` ou `/usr/bin/chromium-browser`.

## Workflow standard

### 1. Créer un projet Remotion

```bash
# Dans un dossier vide
npx create-video@latest --yes --blank --no-tailwind .
npm i
```

Si le dossier n'est pas vide, créer un sous-dossier :
```bash
npx create-video@latest --yes --blank --no-tailwind mon-projet
cd mon-projet
npm i
```

### 2. Structure d'une composition (vidéo)

```tsx
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate } from 'remotion';

export const MaComposition: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const opacity = interpolate(frame, [0, 30], [0, 1]);

  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1a2e' }}>
      <div style={{ opacity, fontSize: 60, color: 'white' }}>
        Texte animé
      </div>
    </AbsoluteFill>
  );
};
```

### 3. Structure multi-séquence

```tsx
export const Video: React.FC = () => {
  return (
    <>
      <Sequence durationInFrames={90} from={0}>
        <Scene1 />
      </Sequence>
      <Sequence durationInFrames={90} from={90}>
        <Scene2 />
      </Sequence>
    </>
  );
};
```

### 4. Démarrer le studio de prévisualisation

```bash
npx remotion studio --no-open
# URL: http://localhost:3000
```

### 5. Rendre la vidéo

```bash
# Lister les compositions disponibles
npx remotion compositions

# Rendre une composition
npx remotion render MaComposition --output out/video.mp4
```

## Cas d'usage pour Pierre

| Type | Description | Composants clés |
|------|-------------|----------------|
| **Daily AI Brief video** | Top 5 news animé → YouTube Short | `Sequence`, `spring`, `interpolate`, sous-titres |
| **Promo app** | Explainer animé pour Vaulty/Budget | Textes, transitions, screenshots |
| **Intro signature** | 5s animée pour Dark Chronicles | Logo, texte fondu, musique |
| **Rapport animé** | Stats qui se construisent | `useVideoConfig`, barres animées, légendes |
| **Réseaux sociaux** | Annonce produit / teasing | Format 1:1, 16:9, 9:16 |

## API clés

| API | Usage |
|-----|-------|
| `useCurrentFrame()` | Frame courante (0, 1, 2...) |
| `useVideoConfig()` | `{ width, height, fps, durationInFrames }` |
| `<Sequence>` | Sous-vidéo dans une plage de frames |
| `interpolate()` | Mapper une valeur sur un intervalle |
| `spring()` | Animation physique (ressort) |
| `<Img>, <Video>, <Audio>` | Assets media |
| `@remotion/player` | Embedder le player dans une app React |

## Recherche doc

```bash
POST https://plsduol1ca-dsn.algolia.net/1/indexes/*/queries?x-algolia-api-key=3e42dbd4f895fe93ff5cf40d860c4a85&x-algolia-application-id=PLSDUOL1CA
{ "requests": [{ "query": "<terme>", "indexName": "remotion" }] }
```

## Pièges

- **Chromium nécessaire** — vérifier qu'il est installé AVANT le rendu
- **Rendu lent** — image par image, proportionnel à la durée et la complexité
- **Ne pas confondre avec ffmpeg** — Remotion est pour l'animation, pas l'assemblage de clips
- **Version** — Les API changent, `npx remotion --version`
- **Stockage** — Les vidéos prennent de la place, nettoyer `out/`
- **Pas un service** — S'exécute ponctuellement, pas de process en fond
- **Port conflit** — `npx remotion studio --port 3001 --no-open`

## Licence

Remotion est gratuit pour les individus et organisations ≤3 employés. Pas besoin de licence pour l'usage de Pierre.