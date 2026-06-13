# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A curated question bank for a daily-learning system. Questions are designed to reveal non-obvious answers about ordinary things — each one should produce a genuine "huh" moment, be answerable from a single good page, and never give the answer away in the question itself.

Two files:

- **`question-bank.md`** — 80 starter questions across 8 domains (kitchen & food, the body, household objects, social customs & language, money & everyday systems, nature & weather, everyday tech, games & puzzles), 10 per domain.
- **`question-bank-science.md`** — 50 more across 5 science-leaning domains (medicine & health, biology & the living world, earth & geology, math & numbers, space & sky), 10 per domain.

## The question bar

Every question must pass all four of these:

1. **Specific** — asks about one concrete thing, not a broad topic.
2. **Non-obvious answer** — most people don't already know it or half-know it.
3. **Findable** — answerable from one decent page; no deep research required.
4. **Self-concealing** — reading the question doesn't give away the answer.

"Why is the sky blue?" is borderline — most people half-know it. That's the low-water mark, not the target.

## Adding questions

When generating new questions for an existing domain, treat the existing questions in that domain as style anchors — they set the bar and prevent repeats. Feed the relevant set to the generator alongside the full recent-questions list to avoid accidental duplication.

## Adding a new domain

1. Pick 8–10 hand-written starters that clearly clear the bar for that domain.
2. Add them as a new section in one of the question bank files (or a new file for a thematic grouping).
3. Note the domain name so it can be added to the rotation in whatever system consumes these files.

The first handful of hand-tuned questions per domain are the only thing that ever needs manual curation — everything else extends from them.

<!-- GSD:project-start source:PROJECT.md -->
## Project

**Daily Learning — n8n Email Workflow**

A single n8n workflow that sends 3 curiosity questions by email every morning at 06:30. Questions are drawn from a static bank of 130 hand-curated questions stored in a Google Sheet. The workflow picks the 3 oldest unsent questions, emails them via Gmail, and marks them sent.

**Core Value:** A question lands in the inbox every morning — no setup friction, no AI dependency, no gaps.

### Constraints

- **Platform**: n8n (self-hosted or cloud) — workflow must use n8n node types
- **Email**: Gmail via OAuth
- **Sheet**: Google Sheets — single Bank tab
- **No AI in workflow**: Workflow is static logic only; Claude is not called at runtime
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
