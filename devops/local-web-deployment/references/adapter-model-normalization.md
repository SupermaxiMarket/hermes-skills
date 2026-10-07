# Hermes Gateway Adapter — Model Name Normalization

## Problem

The Hermes3D Studio frontend sends model names in the format:
```
hermes/deepseek/deepseek-v4-flash:0731-cloud
```

The `resolveHermesModel()` function in `server/hermes-gateway-adapter.js` splits by `/` and takes the last segment:
```
deepseek-v4-flash:0731-cloud
```

This model name does NOT exist on OpenRouter. The actual model is:
```
deepseek/deepseek-v4-flash-0731
```

The colon (`:`) is not a valid separator in OpenRouter model IDs, and the `-cloud` suffix is non-standard.

## Fix

In `server/hermes-gateway-adapter.js`, locate `resolveHermesModel()` (~line 395) and add normalization after the split:

```javascript
async function resolveHermesModel(requestedModel) {
  const trimmed = typeof requestedModel === "string" ? requestedModel.trim() : "";
  let normalized = trimmed.includes("/") ? trimmed.split("/").pop().trim() : trimmed;
  // Normalize model names: replace ":" with "-" and strip "-cloud" suffix
  normalized = normalized.replace(/:/g, "-").replace(/-cloud$/i, "");
  // ... rest of function
```

The normalization converts:
- `deepseek-v4-flash:0731-cloud` → `deepseek-v4-flash-0731` ✅
- `deepseek-v4-flash:0731` → `deepseek-v4-flash-0731` ✅
- `deepseek-v4-flash` → `deepseek-v4-flash` (unchanged) ✅

## Root cause

Le frontend Studio utilise le préfixe `hermes/` quand il envoie le modèle au gateway. L'adapter extrait correctement le suffixe, mais le nom exact du modèle sur OpenRouter utilise des tirets (`-`) là où le Studio utilise des deux-points (`:`) et ajoute un suffixe `-cloud` qui n'existe pas dans l'API. La normalisation est donc nécessaire pour aligner les deux naming conventions.

## Note

Ce fichier (`server/hermes-gateway-adapter.js`) est versionné — la normalisation sera perdue au prochain `git pull`. La conserver localement ou la proposer en PR upstream.