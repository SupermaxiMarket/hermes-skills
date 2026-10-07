#!/usr/bin/env python3
"""
web-to-obsidian skill: listen to Telegram messages (URLs or plain text)
and save them as markdown files in the Obsidian vault under 04-Archives/WebClips/
with appropriate tags.
"""

import os
import time
import json
import requests
from urllib.parse import urlparse

# Hermes tools
try:
    from hermes_tools import web_extract, write_file
except ImportError:
    # Fallback for testing outside Hermes environment
    def web_extract(urls):
        return {"results": [{"url": u, "title": "", "content": f"[Fallback extraction for {u}]", "error": None} for u in urls]}
    def write_file(path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"path": path}

# Configuration from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "/root/obsidian-vault")
WEB_CLIP_DIR = os.path.join(VAULT_PATH, "04-Archives", "WebClips")
POLL_INTERVAL = int(os.getenv("WEB_TO_OBSIDIAN_POLL", "5"))  # seconds

# Ensure output directory exists
os.makedirs(WEB_CLIP_DIR, exist_ok=True)

# Telegram API base
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def get_updates(offset=None):
    """Fetch new updates from Telegram."""
    params = {"timeout": 30, "limit": 100}
    if offset:
        params["offset"] = offset
    try:
        resp = requests.get(f"{TELEGRAM_API}/getUpdates", params=params, timeout=35)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[web-to-obsidian] Telegram error: {e}")
        return {"ok": False, "result": []}

def is_url(text):
    """Heuristic to detect if a string is a URL."""
    stripped = text.strip()
    return stripped.startswith("http://") or stripped.startswith("https://")

def extract_domain(url):
    """Extract domain without www. for tagging."""
    try:
        hostname = urlparse(url).hostname
        if hostname:
            if hostname.startswith("www."):
                hostname = hostname[4:]
            return hostname.replace(".", "-")
    except Exception:
        pass
    return None

def build_frontmatter(tags, title=None):
    """Create YAML frontmatter for Obsidian."""
    lines = ["---"]
    if title:
        lines.append(f"title: {title}")
    lines.append("tags:")
    for tag in tags:
        lines.append(f"  - {tag}")
    lines.append("---\n")
    return "\n".join(lines)

def process_message(message):
    """Handle a single Telegram message."""
    chat_id = message.get("chat", {}).get("id")
    # Only process messages from the configured chat (if set)
    if TELEGRAM_CHAT_ID and str(chat_id) != TELEGRAM_CHAT_ID:
        return
    text = message.get("text", "").strip()
    if not text:
        return

    print(f"[web-to-obsidian] Received message: {text[:80]}...")
    tags = ["webclip", "source:telegram"]
    filename_base = time.strftime("%Y-%m-%d_%H-%M-%S")
    content_parts = []

    if is_url(text):
        url = text
        tags.append("source:url")
        domain_tag = extract_domain(url)
        if domain_tag:
            tags.append(domain_tag)
        print(f"[web-to-obsidian] Extracting URL: {url}")
        extraction = web_extract([url])
        results = extraction.get("results", [])
        if results and not results[0].get("error"):
            extracted = results[0]
            title = extracted.get("title") or url
            content = extracted.get("content", "")
            # Try to get a sensible title from content if missing
            if not title or title == url:
                # extract first line that looks like a heading
                for line in content.split("\n"):
                    if line.strip():
                        title = line.strip()[:100]
                        break
                if not title:
                    title = "Web Clip"
            content_parts.append(f"# {title}\n")
            content_parts.append(content)
            content_parts.append(f"\n\n*Source:* [{url}]({url})")
        else:
            err = results[0].get("error") if results else "Unknown error"
            print(f"[web-to-obsidian] Extraction failed for {url}: {err}")
            content_parts.append(f"# Web Clip (URL extraction failed)\n")
            content_parts.append(f"URL: {url}\n")
            content_parts.append(f"*Error:* {err}")
    else:
        # Treat as plain text / tweet
        tags.append("source:tweet")
        content_parts.append(f"# Telegram Note\n")
        content_parts.append(text)
        content_parts.append(f"\n\n*Sent via Telegram at* {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Build frontmatter
    frontmatter = build_frontmatter(tags, title=content_parts[0].replace("# ", "").strip() if content_parts else None)
    markdown = frontmatter + "\n".join(content_parts)

    # Create filename
    filename = f"{filename_base}_webclip.md"
    out_path = os.path.join(WEB_CLIP_DIR, filename)
    print(f"[web-to-obsidian] Writing to {out_path}")
    write_file(out_path, markdown)
    print(f"[web-to-obsidian] Successfully saved.")

def main():
    print("[web-to-obsidian] Starting web-to-obsidian skill...")
    if not TELEGRAM_BOT_TOKEN:
        print("[web-to-obsidian] Error: TELEGRAM_BOT_TOKEN not set.")
        return
    if not TELEGRAM_CHAT_ID:
        print("[web-to-obsidian] Warning: TELEGRAM_CHAT_ID not set; will accept messages from any chat.")
    offset = None
    while True:
        try:
            updates = get_updates(offset=offset)
            if updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        process_message(update["message"])
            else:
                print("[web-to-obsidian] Failed to get updates")
        except Exception as e:
            print(f"[web-to-obsidian] Unexpected error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()