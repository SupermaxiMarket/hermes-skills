# LinkedIn DOM Notes (Session 2026-06-03)

Observed while debugging the LinkedIn Comment Generator plugin.

## Feed Container
- The main infinite scroll feed is a `<div>` with class `scaffold-finite-scroll__content`.
- Each post entry is a direct child of this container.

## Post Element Selectors that worked (as of this session)
1. `div[data-test-id="feed-update"]` – most stable, present on nearly all posts.
2. `div[data-urn*="activity"]:has(.feed-shared-update-v2)` – combines URN with class guard.
3. `.feed-shared-update-v2` – historic class, still present.
4. `.occludable-update.feed-shared-update-v2` – variant with additional occlusion class.
5. `.artdeco-card.feed-shared-update-v2` – fallback generic.

## Attributes of Interest
- `data-urn` format: `urn:li:activity:<numeric-id>`.
- `data-test-id` values: `"feed-update"`, `"comment-social-actions"`, etc.
- `aria-label` sometimes contains the post author name.

## Common Variations
- Sponsored posts add class `feed-shared-sponsored-update`.
- Some posts (e.g., polls) wrap the content in additional `<div>` layers but still retain the core classes above.
- Posts lacking `data-test-id` but having `data-urn*="activity"` still match selectors 2-5.

## Recommended Approach
- Use a prioritized selector list (see skill).
- Always filter for `offsetParent !== null` and non-zero bounding box to ignore hidden elements.
- Mark processed posts with a dataset flag (e.g., `data-lcg-processed="true"`).

## Observed Console Messages from Original Plugin
- `LinkedIn Comment Generator: Trouvé 0 posts avec le sélecteur div[data-urn*="activity"]`
- `LinkedIn Comment Generator: Trouvé 0 posts avec le sélecteur article[data-urn]`
- `LinkedIn Comment Generator: Trouvé 0 posts avec le sélecteur .feed-shared-update-v2`

These indicated that the selectors were too specific or the DOM changed.

## Additional Notes
- LinkedIn occasionally wraps posts in a `<div class="relative">` or similar; the selectors above still match inner elements.
- MutationObserver is essential for detecting new posts as the user scrolls.
- Some ad blockers remove `data-test-id` attributes; having fallback selectors mitigates this.