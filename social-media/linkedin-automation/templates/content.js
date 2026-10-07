/* ==============================================================
   LinkedIn Comment Generator – content.js
   Boilerplate following the linkedin-automation skill workflow
   --------------------------------------------------------------
   Replace the placeholder logic with your actual comment generation.
   ============================================================== */

(function () {
    'use strict';

    const SETTINGS = {
        retryDelay: 1500,
        maxRetries: 8,
        processedMarker: 'lcg-processed'
    };

    const POST_SELECTORS = [
        'div[data-test-id="feed-update"]',
        'div[data-urn*="activity"]:has(.feed-shared-update-v2)',
        '.feed-shared-update-v2',
        '.occludable-update.feed-shared-update-v2',
        '.artdeco-card.feed-shared-update-v2'
    ];

    function isElementVisible(el) {
        const rect = el.getBoundingClientRect();
        return el.offsetParent !== null &&
               rect.width > 0 &&
               rect.height > 0 &&
               rect.top >= -rect.height &&
               rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + rect.height;
    }

    function getFreshPostElements() {
        const candidates = [];
        POST_SELECTORS.forEach(sel => {
            try {
                document.querySelectorAll(sel).forEach(node => {
                    if (isElementVisible(node) && !node.dataset[SETTINGS.processedMarker]) {
                        candidates.push(node);
                    }
                });
            } catch (e) {
                console.warn(`[LCG] Invalid selector "${sel}":`, e);
            }
        });
        return [...new Set(candidates)];
    }

    function processPost(postElement) {
        try {
            postElement.dataset[SETTINGS.processedMarker] = 'true';

            // ======================
            // PUT YOUR LOGIC HERE
            // Example: add a button to generate a comment
            // ======================
            const btn = document.createElement('button');
            btn.textContent = 'Generate Comment';
            btn.style.marginTop = '8px';
            btn.style.padding = '4px 8px';
            btn.style.background = '#0a66c2';
            btn.style.color = '#fff';
            btn.style.border = 'none';
            btn.style.borderRadius = '3px';
            btn.style.cursor = 'pointer';

            btn.addEventListener('click', () => {
                // Replace with actual comment generation
                alert('Comment generation logic goes here!');
            });

            const header = postElement.querySelector('.feed-shared-header, .feed-shared-update-v2__description');
            if (header) {
                header.parentNode.insertBefore(btn, header.nextSibling);
            } else {
                postElement.appendChild(btn);
            }
            // ======================
            // END OF YOUR LOGIC
            // ======================

            console.info('[LCG] Post processed', postElement);
        } catch (err) {
            console.error('[LCG] Error processing post:', err, postElement);
        }
    }

    let attempts = 0;
    function detectAndProcess() {
        const posts = getFreshPostElements();
        if (posts.length > 0) {
            console.info(`[LCG] ${posts.length} new post(s) detected`);
            posts.forEach(processPost);
            attempts = 0;
        } else if (attempts < SETTINGS.maxRetries) {
            attempts++;
            setTimeout(detectAndProcess, SETTINGS.retryDelay);
        } else {
            console.error('[LCG] Failed to detect posts after several attempts.');
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', detectAndProcess);
    } else {
        detectAndProcess();
    }

    const observer = new MutationObserver(mutations => {
        const fresh = getFreshPostElements();
        if (fresh.length) fresh.forEach(processPost);
    });
    observer.observe(document.body, { childList: true, subtree: true });

    window.__lcgStop = () => {
        observer.disconnect();
        console.info('[LCG] Observer stopped.');
    };
})();