---
name: cron-jobs
description: "Create and run cron jobs with no_agent scripts and pitfalls."
version: 1.0.0
platforms: [linux]
---

# Cron Jobs — Hermes Scheduling

Create, manage, and troubleshoot recurring cron jobs via `cronjob` tool.

## Key Concepts

### Agent mode (default)

The job runs as a full Hermes agent with LLM reasoning. The prompt is the task instruction. Skills can be attached via `--skills`.

```bash
# Create a daily briefing
cronjob action=create schedule="0 8 * * *" \
  prompt="Summarize today's top 5 AI news and deliver as a brief" \
  skills=["daily_ai_brief"] deliver=telegram
```

### Script mode (`no_agent=True`)

The job runs a script **without** an LLM loop. No tokens consumed. The script's stdout is delivered verbatim.

```bash
cronjob action=create schedule="every 6h" \
  no_agent=True script=news-fetcher.py deliver=local
```

## ⚠️ Pitfalls

### `no_agent=True` scripts cannot import `hermes_tools`

The `hermes_tools` module (`web_search`, `web_extract`, `read_file`, etc.) is **only available inside a running Hermes agent session**. Scripts launched with `no_agent=True` run as standalone Python processes outside the agent runtime — they will crash with:

```
ModuleNotFoundError: No module named 'hermes_tools'
```

**Fix:** Use plain Python libraries instead:
- `requests` + RSS (Google News RSS, etc.) instead of `web_search`
- `urllib.request` + HTML parsers instead of `web_extract`
- `os`, `json`, `re`, `datetime` etc. are always available

### `input()` blocks in terminal/PTY

Calling `input()` in a cron job or in a terminal started with `background=True` will get `EOFError: EOF when reading a line` because there's no stdin. If a script needs user input:

1. Pass the value as a command-line argument (`sys.argv[1]`)
2. Accept it via the cron prompt (agent mode) or environment variable (script mode)

### Script mode delivery semantics

- Non-empty stdout → delivered verbatim
- Empty stdout → **silent** — nothing is sent. Design watchdogs to stay quiet when there's nothing to report.
- Non-zero exit / timeout → error alert sent to the user

### Token expiry in `no_agent=True` scripts

Scripts cannot use Hermes-managed tokens or credentials. API keys, OAuth tokens, and env vars must be managed directly inside the script (read from `.env`, filesystem, etc.).

## Useful patterns

| Pattern | Example |
|---------|---------|
| Watchdog | `no_agent=True`, script exits with 0 + empty stdout when all is well, non-zero + message when something's wrong |
| Data collection | `no_agent=False` (agent mode), script output is injected into the prompt as context |
| Chained jobs | Use `context_from` to pipe one job's output into the next job's prompt |
| Project-specific | Set `workdir=/root/projets/foo` to load project context files (AGENTS.md, CLAUDE.md) |
| **Minimal tools** | Use `enabled_toolsets` to restrict tools to only what the job needs — e.g. `enabled_toolsets=["web"]` for monitoring-only jobs saves significant input tokens vs loading all default tools |

### Pattern: minimal-tool monitoring cron

For recurring monitoring/digest jobs that only need web search, restrict toolsets to save tokens:

```
cronjob action=create schedule="0 7 * * *" \
  enabled_toolsets=["web"] \
  prompt="[your monitoring prompt]"
```

This loads only `web_search` and `web_extract` instead of the full tool suite — cuts token overhead by skipping terminal, file, code_exec, etc.

## References

- `references/lightweight-ocr-fallback.md` — extract text from image-based PDFs and screenshots when the model lacks vision (tesseract + pymupdf, no PyTorch required)

## Troubleshooting

- `cronjob action=list` — see all jobs with status, last run, next run
- `cronjob action=run <job_id>` — force-run a job immediately
- A job stuck in "scheduled" state never reached its next tick — check `last_status` field
- Script jobs: the `last_delivery_error` field shows the stderr output if the script crashed