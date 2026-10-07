---
name: hermes-astros
description: "Hermes Astros - Automated competitor research and content idea generation system"
version: 1.0.0
author: Hermes Agent + Pierre Andre Erard
license: MIT
category: autonomous-ai-agents
---
# Hermes Astros Skill

This skill encapsulates the Hermes Astros system demonstrated in the YouTube video: an automated competitor research and content idea generation system built on the Hermes Agent Operating System.

## Overview

Hermes Astros is a system that:
- Uses Google Workspace API (via Hermes agent) to monitor keywords, competitors, and topics
- Runs on a schedule (default: every 4 hours) to scan for trending content
- Generates unique content angles, titles, and recommendations based on trending topics
- Syncs all findings to Obsidian memory so all agents in the system are aware of current research
- Can generate SEO content, video scripts, notebooks, and other content formats with one click
- Integrates with video agent, Notebook LM, and other Hermes tools for end-to-end content creation

## Features

- **Competitor Radar**: Monitors specified content creators and keywords
- **Trend Scoring**: Scores content by virality/potential
- **Unique Angle Generation**: Provides unique titles and hooks based on your niche
- **One-Click Content Generation**: 
  - SEO blog posts via SEO skill
  - Video scripts via video agent
  - NotebookLM notebooks
  - Infographics, mind maps, flashcards, etc. via NotebookLM integration
- **Memory Synchronization**: All research is logged to Obsidian, creating a searchable trending archive
- **Fully Customizable**: Watch lists, keywords, competitors, schedule, and output formats are fully customizable

## Setup

1. **Prerequisites**:
   - Hermes Agent installed and configured
   - Google Workspace API access configured (via Hermes model/tools)
   - Obsidian vault connected to Hermes memory (optional but recommended)
   - Optional: Video agent, NotebookLM, SEO skills for full functionality

2. **Install the skill**:
   ```bash
   hermes skills install https://raw.githubusercontent.com/NousResearch/hermes-agent/main/skills/autonomous-ai-agents/hermes-astros/SKILL.md
   ```

3. **Configure**:
   - Edit `~/.hermes/skills/autonomous-ai-agents/hermes-astros/prompts/system.md` to set your niche, keywords, competitors
   - Adjust schedule in `hermes cron` if desired (default: every 4 hours)
   - Enable required toolsets: `web`, `terminal`, `file`, `memory`

4. **Usage**:
   - Trigger manually: `/scan-skies` (or run the cron job manually)
   - View results in Obsidian memory or via `/astros-report`
   - Generate content: `/create-content <topic>` or use the UI elements in the Hermes TUI

## Commands

- `/astros-status` - Show current configuration and last run status
- `/scan-skies` - Trigger an immediate scan
- `/astros-report` - Show latest research report
- `/create-content <topic>` - Generate content ideas for a topic
- `/astros-watchlist add <keyword>` - Add a keyword to monitor
- `/astros-watchlist remove <keyword>` - Remove a keyword
- `/astros-competitor add <name>` - Add a competitor/creator to monitor
- `/astros-competitor remove <name>` - Remove a competitor

## How It Works

1. **Scheduled Scan**: The cron job (or manual trigger) activates the Astros agent
2. **Research Phase**: Uses Google Workspace API to search for recent content matching watchlist
3. **Analysis Phase**: Hermes agent analyzes content for:
   - Virality signals (views, engagement, shares)
   - Topic categorization
   - Content gaps and opportunities
4. **Angle Generation**: Generates unique titles, hooks, and content angles tailored to your niche
5. **Memory Sync**: Results are saved to Obsidian memory with metadata (timestamp, source, score)
6. **Content Ready**: Generated angles are ready for one-click conversion to blogs, videos, notebooks, etc.

## Customization

### Prompts
Edit `prompts/system.md` to customize:
- Your niche/industry focus
- Tone and style preferences
- Content format preferences
- Scoring criteria

### Templates
Edit `templates/` to change output formats for:
- SEO blog outlines
- Video scripts
- NotebookLM notebooks
- Social media posts

### Scripts
Customize the research logic in `scripts/` if you need to integrate additional APIs or change the research methodology.

## Example Workflow

1. User runs `/scan-skies` or waits for scheduled scan
2. Astros scans Google Workspace for recent content about "AI SEO", "Claude Code", etc.
3. Finds a trending article about "AI-powered SEO techniques"
4. Analyzes: high engagement, recent, in SEO niche
5. Generates unique angle: "How to Use Claude Code for Real-Time SEO Audits That Actually Work"
6. Saves to Obsidian: `2026-07-05 - AI SEO Angles.md` with summary and source links
7. User runs `/create-content "AI SEO audits with Claude"` 
8. System suggests: 
   - SEO blog outline targeting that keyword
   - Video script outline for a tutorial
   - NotebookLM notebook for deep research
9. User selects video agent → generates full video with AI avatar, B-roll, voiceover
10. All activity logged to Obsidian for team visibility

## Dependencies

- Hermes Agent with web, terminal, file, memory toolsets enabled
- Google Workspace API credentials configured in Hermes
- Optional but recommended:
  - Video agent skill
  - NotebookLM integration
  - SEO content skill
  - Obsidian memory provider

## Troubleshooting

- **No results**: Check Google Workspace API configuration and quota
- **Memory not syncing**: Verify Obsidian vault path in Hermes memory settings
- **Slow scans**: Adjust search recency or reduce watchlist size in prompts
- **Generic outputs**: Refine your niche description and examples in `prompts/system.md`

## Extending the System

This skill is designed to be extended:
- Add new content templates in `templates/`
- Add new research sources in `scripts/`
- Create new slash commands by extending the skill's command handlers
- Integrate with other MCP servers for additional data sources

---
*This skill encapsulates the Hermes Astros system as demonstrated in the YouTube video, adapted for the Hermes Agent Operating System.*