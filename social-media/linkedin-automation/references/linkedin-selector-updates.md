# LinkedIn Selector Updates (Session 2026-06-22)

Observed that LinkedIn frequently changes DOM selectors. The following selectors have been found effective for detecting posts, content, and comment fields as of this session.

## Post Container Selectors
- `div[data-test-id="feed-update"]` (legacy test attribute)
- `div[data-testid="feed-update"]` (modern test attribute)
- `div[data-urn*="activity"]:has(.feed-shared-update-v2)`
- `.feed-shared-update-v2`
- `.occludable-update.feed-shared-update-v2`
- `.artdeco-card.feed-shared-update-v2`
- `div[role="article"]` (semantic fallback)

## Post Content Selectors
- `.feed-shared-text`
- `.feed-shared-update-v2__description`
- `.feed-shared-text-view`
- `.attributed-text-segment-list__content`
- `.break-words`
- `.feed-shared-text-view__text-content`
- `.feed-shared-update-v2__description-wrapper .break-words`
- `.feed-shared-text-view .break-words`
- `.feed-shared-update-v2__description .break-words`
- `[data-testid="post-text"]`
- `div[dir="ltr"] span[aria-hidden="false"]`

## Comment Field Selectors
- `.ql-editor[data-placeholder*="commentaire"]`
- `.ql-editor[data-placeholder*="Comment"]`
- `.ql-editor[contenteditable="true"]`
- `textarea[placeholder*="commentaire"]`
- `textarea[placeholder*="Comment"]`
- `.comments-comment-box__form textarea`
- `.comments-comment-box-comment__text-editor`
- `.ql-editor`
- `div[contenteditable="true"]`
- `[role="textbox"]`
- `[data-testid="comment-editor"]`

These selectors can be added to the respective arrays in the boilerplate `content.js` template to improve resilience against LinkedIn UI updates.