---
name: linkedin-automation
category: social-media
description: Guidelines for developing, debugging, and maintaining LinkedIn browser extensions, userscripts, or content scripts that interact with the LinkedIn feed.
---

**Description**: Guidelines for developing, debugging, and maintaining LinkedIn browser extensions, userscripts, or content scripts that interact with the LinkedIn feed (e.g., comment generators, reaction bots, analytics tools). Covers selector robustness, handling infinite scroll, avoiding double processing, and dealing with LinkedIn's frequent DOM changes.

## When to Use
- You need to read or modify LinkedIn feed posts via a content script or extension.
- You observe that selectors like `div[data-urn*="activity"]` stop returning elements.
- You want to reliably detect newly loaded posts as the user scrolls.
- You must ensure your script does not execute multiple times on the same post.

## Trigger Conditions
- The task involves LinkedIn DOM manipulation.
- The user reports "0 posts found with selector …" or similar console warnings.
- The script works initially but fails after a LinkedIn UI update.
- You are updating an existing LinkedIn plugin/userscript.

## Step‑by‑Step Workflow

### 1. Audit the Current DOM
1. Open LinkedIn, scroll to load a few posts.
2. Open DevTools → Elements.
3. Inspect a post container and note:
   - Stable attributes (`data-test-id`, `data-urn`, `aria-label`, etc.).
   - Consistent class names (e.g., `feed-shared-update-v2`, `occludable-update`).
   - Whether the element is a direct child of the scrollable feed or nested.

### 2. Choose Robust Selectors
Use a **priority list** of selectors, ordered from most specific to most generic. Example:
```js
const POST_SELECTORS = [
  'div[data-test-id="feed-update"]',                     // UI‑test attribute (most stable)
  'div[data-urn*="activity"]:has(.feed-shared-update-v2)', // data‑urn + class guard
  '.feed-shared-update-v2',                              // historic class
  '.occludable-update.feed-shared-update-v2',           // variant with occlusion
  '.artdeco-card.feed-shared-update-v2'                 // fallback generic
];
```
- If any selector uses `:has()` and your target browser does not support it, replace with a two‑step query (first match `[data-urn*="activity"]`, then filter for `.feed-shared-update-v2` descendant).

### 3. Visibility Filter
Only process elements that are actually rendered:
```js
function isElementVisible(el) {
  const rect = el.getBoundingClientRect();
  return el.offsetParent !== null &&
         rect.width > 0 &&
         rect.height > 0 &&
         rect.top >= -rect.height &&
         rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + rect.height;
}
```

### 4. Avoid Double Processing
Add a dataset flag once a post has been handled:
```js
if (!el.dataset.lcgProcessed) {
  el.dataset.lcgProcessed = 'true';
  // … your logic …
}
```

### 5. Initial Detection Loop
Run a detection function on page load and after short retries:
```js
let attempts = 0;
const MAX_ATTEMPTS = 8;
const RETRY_DELAY = 1500; // ms

function detectAndProcess() {
  const posts = getFreshPosts(); // implements selectors + visibility + dedup
  if (posts.length) {
    posts.forEach(processPost);
    attempts = 0; // reset on success
  } else if (attempts < MAX_ATTEMPTS) {
    attempts++;
    setTimeout(detectAndProcess, RETRY_DELAY);
  } else {
    console.error('[LinkedIn Automation] Failed to detect posts after several attempts.');
  }
}
```
Call `detectAndProcess` on `DOMContentLoaded` or immediately if `document.readyState` is not `"loading"`.

### 6. Handle Infinite Scroll with MutationObserver
```js
const observer = new MutationObserver(mutations => {
  const fresh = getFreshPosts();
  if (fresh.length) fresh.forEach(processPost);
});
observer.observe(document.body, { childList: true, subtree: true });
```
- Optionally disconnect on page unload or when the user disables the feature.

### 7. Post‑Processing Logic
Place your core functionality (e.g., generating a comment, inserting a button) inside `processPost(postElement)`. Keep it isolated from detection logic.

### 8. Debugging & Logging
- Log the number of posts found at each detection cycle.
- Log which selector matched a given post (helps when LinkedIn changes).
- In case of zero matches, output the current HTML of the feed container to inspect for structural changes.

## Common Pitfalls & How to Avoid Them
| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Over‑reliance on a single selector (e.g., only `data-urn*="activity"` ) | Script stops working after LinkedIn updates attribute placement | Use a selector list with fallbacks (see §2). |
| Missing visibility check | Script processes hidden or off‑screen elements, causing duplicate actions | Add `isElementVisible()` filter. |
| No deduplication | Same post processed multiple times on scroll or network retry | Set a `data‑lcg‑processed` flag. |
| Ignoring lazy‑loaded images/scripts | Layout shifts cause missed posts | Use `MutationObserver` as in §6. |
| CSP blocking LinkedIn scripts | Console shows blocked requests, script fails to load | Ensure your extension’s CSP allows `https://www.linkedin.com` or request the needed permissions. |
| Using outdated jQuery or other libs | Errors like `$ is not defined` | Either remove dependency or bundle a compatible version. |
| Overly aggressive retry loops | High CPU usage, page lag | Cap retries (`MAX_ATTEMPTS`) and use reasonable delay (`RETRY_DELAY`). |
| Using multiline template literals for SVG `innerHTML` | CSP or parsing errors like `Error: <path> attribute d: Expected number, ...` | Keep SVG markup as a single‑line string (no line breaks) or use `innerHTML = svgString` where `svgString` has no newline characters; avoid template literals that introduce whitespace inside the `<path d=...>` |

## Reference Files
- `references/linkedin-dom-notes.md` – Observed LinkedIn feed structure (as of 2024‑06) and selector effectiveness.
- `references/linkedin-selector-updates.md` – Selector updates from session 2026-06-22 (post, content, comment field selectors).
- `templates/content.js` – Boilerplate content‑script implementation following the workflow above.

## Version History
- **v1.0** – Initial creation (2026‑06‑03): robust selector list, visibility filter, deduplication, MutationObserver, retry loop.

---
*This skill is intended to be consulted whenever you need to build or fix a LinkedIn‑targeted browser extension or userscript. It encapsulates the lessons learned from debugging the “LinkedIn Comment Generator” plugin and similar tools.*