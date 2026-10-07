# Julian Goldie Agent OS Setup Reference

## Key Points from Videos and Posts

- **Dual Ports**:
  - `localhost:3000` : Direct Hermes interface (or local LLM via Ollama/LM Studio)
  - `localhost:3737` : Mission Control Dashboard (JS) showing agent status in sidebar

- **Seven-Layer Architecture** (from "Build Your Own Agent Operating System" video):
  1. Foundation (WSL/Linux)
  2. Memory (Obsidian + OMI transcripts)
  3. Brain (routed models: Claude / Claude Code as CEO)
  4. Agents (Hermes, OpenClaw, etc. as specialists)
  5. Command Center (Next.js Mission Control Dashboard)
  6. Production Surfaces (studio/SEO/goals/workspaces)
  7. Feedback Loop (outputs written back to memory)

- **Core Philosophy**:
  - Agent OS connects scattered AI tools into one coherent system with shared memory, context, and coordinated workflows.
  - Without OS: Apps work in isolation (like a phone without iOS/Android).
  - With OS: Agents share state, coordinate automatically, and build compounding intelligence over time.

- **Memory Layer Details**:
  - Uses Obsidian vault for permanent personal context (Self layer).
  - OMI transcripts (audio logs) can feed into Obsidian for voice context.
  - Every agent output is automatically logged back into the vault, creating accumulating context.

- **Workflow Example**:
  - User interacts via Mission Control dashboard (port 3737).
  - Dashboard routes tasks via OpenClaw (execution layer) to appropriate agents.
  - Hermes (research layer) performs multi-step workflows, tool calls, Kanban, skills.
  - Results flow back to dashboard and are saved to Obsidian memory.
  - Next day, agents start with full context from prior work.

- **Practical Setup Mentioned**:
  - Hermes Agent + OpenClaw + Obsidian as core free stack.
  - Optional: local models via Ollama/LM Studio to reduce API costs.
  - Dashboard shows live agent status, enabling background job monitoring.

## Relevance to Hermes Agent OS Integrator Skill

This skill establishes the foundation (WSL), memory (Obsidian vault), brain (current model config), agents (existing skills), command center (Hermes TUI/dashboard), production services (Kanban, content generation), and feedback loop (output logging to vault).

The Julian Goldie reference validates that this approach matches a proven Agent OS blueprint.