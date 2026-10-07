---
name: meta_optimizer
description: Auto-improve Hermes agent skills by analyzing task executions
category: autonomous-ai-agents
author: Pierre Andre Erard
created: 2026-05-18
---

# Meta Optimizer Skill

## Purpose
Continuous self-improvement of agent capabilities through:
- Execution pattern analysis
- Weakness detection
- Automated skill refinement

## Workflow
1. Post-task analysis (session_search + terminal history)
2. Bottleneck identification (process, knowledge, tooling)
3. Skill patching (skill_manage action='patch')
4. Validation (test via delegate_task)

## Auto-Critique Rules
- Flag repetitive user corrections (memory tool)
- Detect inefficient tool chains (terminal + browser_console)
- Identify knowledge gaps (session_search cross-referencing)

## Implementation
Uses:
- cronjob for daily optimization cycles
- execute_code for batch analysis
- delegate_task for parallel validation