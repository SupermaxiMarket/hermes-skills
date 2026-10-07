#!/usr/bin/env python3
"""
Obsidian MOC Generator - Creates a dynamic Map of Content note
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re

# Configuration
VAULT_PATH = Path.home() / "obsidian-vault"
MOC_PATH = VAULT_PATH / "00-Inbox" / "🗺️ Map of Content.md"
INCLUDE_FOLDERS = ["01-Projects", "02-Areas", "03-Resources", "04-Archives", "Journal", "AgentOS"]
EXCLUDE_FOLDERS = [".obsidian", ".trash"]

def get_markdown_files(vault_path):
    """Recursively find all .md files in the vault."""
    md_files = []
    for root, dirs, files in os.walk(vault_path):
        # Modify dirs in-place to skip excluded folders
        dirs[:] = [d for d in dirs if d not in EXCLUDE_FOLDERS and not any(ex in os.path.join(root, d) for ex in EXCLUDE_FOLDERS)]
        for file in files:
            if file.endswith(".md"):
                full_path = Path(root) / file
                md_files.append(full_path)
    return md_files

def get_file_stats(file_path):
    """Get modification time and size."""
    stat = file_path.stat()
    return {
        "modified": datetime.fromtimestamp(stat.st_mtime),
        "size": stat.st_size
    }

def extract_wiki_links(content):
    """Extract [[wiki-style]] links from markdown content."""
    # Pattern for [[link]] or [[link|alias]]
    pattern = r'\[\[([^|\]]+)(?:\|[^\]]+)?\]\]'
    return set(match.group(1).strip() for match in re.finditer(pattern, content))

def extract_tags(content):
    """Extract #tags from markdown content."""
    pattern = r'(?:^|\s)#([a-zA-Z0-9_/\\-]+)'
    return set(match.group(1).lower() for match in re.finditer(pattern, content))

def main():
    print(f"Generating MOC for vault at {VAULT_PATH}")
    
    if not VAULT_PATH.exists():
        print(f"Error: Vault path {VAULT_PATH} does not exist.")
        sys.exit(1)
    
    # Get all markdown files
    md_files = get_markdown_files(VAULT_PATH)
    print(f"Found {len(md_files)} markdown files.")
    
    # Organize by folder
    files_by_folder = {}
    all_links = set()
    all_tags = set()
    file_info = {}  # path -> {modified, size, links, tags}
    
    for file_path in md_files:
        # Determine relative path from vault
        try:
            rel_path = file_path.relative_to(VAULT_PATH)
        except ValueError:
            continue  # Should not happen
        
        # Get first folder component for categorization
        parts = rel_path.parts
        if len(parts) == 0:
            folder = "root"
        else:
            folder = parts[0]
        
        # Only include if folder is in INCLUDE_FOLDERS (or root if we want to handle separately)
        if folder not in INCLUDE_FOLDERS and folder != "":
            # Still process for links/tags but won't appear in category list
            pass
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            continue
        
        stats = get_file_stats(file_path)
        links = extract_wiki_links(content)
        tags = extract_tags(content)
        
        file_info[file_path] = {
            "rel_path": rel_path,
            "folder": folder,
            "modified": stats["modified"],
            "size": stats["size"],
            "links": links,
            "tags": tags,
            "content": content[:200]  # Preview
        }
        
        all_links.update(links)
        all_tags.update(tags)
        
        # Add to folder grouping
        if folder not in files_by_folder:
            files_by_folder[folder] = []
        files_by_folder[folder].append(file_path)
    
    # Determine orphan files (no incoming links detected)
    # Build set of all possible note names (without extension, as they appear in links)
    note_names = set()
    for info in file_info.values():
        # Note name is the filename without .md
        name = info["rel_path"].stem
        note_names.add(name)
        # Also consider potential aliases? We'll keep simple.
    
    # Files with no incoming links (based on simple name matching)
    orphan_files = []
    for file_path, info in file_info.items():
        name = info["rel_path"].stem
        # Check if any other file links to this name
        has_incoming = False
        for other_info in file_info.values():
            if name in other_info["links"]:
                has_incoming = True
                break
        if not has_incoming and len(info["links"]) == 0:
            # No outgoing links either - likely orphan
            orphan_files.append(file_path)
    
    # Generate MOC content
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_ago = now - timedelta(days=7)
    
    lines = []
    lines.append("# 🗺️ Map of Content")
    lines.append("")
    lines.append(f"*Last updated: {now.strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")
    
    # Statistics
    lines.append("## 📊 Statistiques")
    lines.append(f"- **Total notes** : {len(md_files)}")
    today_count = sum(1 for info in file_info.values() if info["modified"].date() == now.date())
    week_count = sum(1 for info in file_info.values() if info["modified"] >= week_ago)
    lines.append(f"- **Notes aujourd'hui** : {today_count}")
    lines.append(f"- **Cette semaine** : {week_count}")
    lines.append(f"- **Notes orphelines potentielles** : {len(orphan_files)}")
    lines.append("")
    
    # By category
    lines.append("## 📁 Par catégorie")
    for folder in INCLUDE_FOLDERS:
        if folder in files_by_folder and files_by_folder[folder]:
            lines.append(f"### {folder} ([[{folder}]])")
            # Sort by modified date descending
            folder_files = sorted(
                files_by_folder[folder],
                key=lambda p: file_info[p]["modified"],
                reverse=True
            )
            for file_path in folder_files[:10]:  # Limit to 10 most recent per category
                info = file_info[file_path]
                link_text = info["rel_path"].stem  # Use filename without extension as link
                lines.append(f"- [[{link_text}]]")
            if len(folder_files) > 10:
                lines.append(f"- *et {len(folder_files) - 10} autres...*")
            lines.append("")
    
    # Recent journal
    lines.append("## 📅 Journal récent")
    journal_files = files_by_folder.get("Journal", [])
    if journal_files:
        journal_sorted = sorted(journal_files, key=lambda p: file_info[p]["modified"], reverse=True)
        for file_path in journal_sorted[:5]:  # Last 5 journal entries
            info = file_info[file_path]
            lines.append(f"- [[{info['rel_path'].stem}]]")
    else:
        lines.append("- *Aucune note de journal trouvée*")
    lines.append("")
    
    # Popular tags
    if all_tags:
        lines.append("## 🏷️ Tags populaires")
        # Count tag occurrences
        tag_counts = {}
        for info in file_info.values():
            for tag in info["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        # Sort by count
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags[:10]:  # Top 10
            lines.append(f"- #{tag} ({count})")
        lines.append("")
    
    # Orphan notes
    if orphan_files:
        lines.append("## 🔗 Notes orphelines (à lier)")
        for file_path in orphan_files[:10]:  # Limit to 10
            info = file_info[file_path]
            lines.append(f"- [[{info['rel_path'].stem}]] *({info['modified'].strftime('%Y-%m-%d')})*")
        if len(orphan_files) > 10:
            lines.append(f"- *et {len(orphan_files) - 10} autres orphelins...*")
        lines.append("")
    else:
        lines.append("## 🔗 Toutes les notes sont liées ! 🎉")
        lines.append("")
    
    # Quick ideas
    lines.append("## ✏️ Idées rapides")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("- [ ] ")
    lines.append("")
    
    # Write MOC file
    MOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    MOC_PATH.write_text("\n".join(lines), encoding='utf-8')
    print(f"✓ MOC generated at {MOC_PATH}")

if __name__ == "__main__":
    main()