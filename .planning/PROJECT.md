# Daily Learning — n8n Email Workflow

## What This Is

A single n8n workflow that sends 3 curiosity questions by email every morning at 06:30. Questions are drawn from a static bank of 130 hand-curated questions stored in a Google Sheet. The workflow picks the 3 oldest unsent questions, emails them via Gmail, and marks them sent.

## Core Value

A question lands in the inbox every morning — no setup friction, no AI dependency, no gaps.

## Current Milestone: v1.1 Deploy

**Goal:** Host n8n on a VPS using Docker so the morning email arrives reliably at 06:30 regardless of whether the local machine is on.

**Target features:**
- VPS provisioned and SSH-accessible
- Docker + docker-compose installed on the VPS
- n8n running in a container with persistent storage and auto-restart
- Workflow, Gmail OAuth, and Sheets credentials re-wired in the hosted n8n instance
- Verified: 06:30 email arrives from VPS

## Requirements

### Validated

- ✓ Google Sheet has a single `Bank` tab with columns: question, domain, est_minutes, status, date_sent — Phase 1
- ✓ Bank tab seeded with all 130 questions from questions.md (status = queued) — Phase 1
- ✓ Single n8n workflow triggers daily at 06:30 — Phase 2
- ✓ Workflow reads Bank tab, filters status = queued, picks 3 oldest — Phase 2
- ✓ Workflow sends those 3 questions via Gmail — Phase 2
- ✓ Workflow marks each sent question: status = sent, date_sent = today — Phase 2
- ✓ Email is plain text, no answers, no hints — just the questions with domain and est_minutes — Phase 2

### Active

- [ ] n8n hosted on a VPS so the workflow runs regardless of local machine state

### Out of Scope

- AI question generation — no Claude API calls in the workflow (future Claude agent handles bank edits)
- Domains tab — domain lives on the question row, no separate tab needed
- Queue depth top-up logic — bank is pre-seeded, no Workflow A equivalent

## Context

- Google Sheet `Bank` tab is live with 130 questions, all status = queued
- n8n workflow `Daily Learning — Morning Questions` (ID: WT359GdOyEqgHsma) is active on local machine
- Gmail OAuth credential wired in n8n — sending to lfornefett@gmail.com
- n8n is local-only — workflow only runs when the machine is on; VPS migration is the next infrastructure step
- A Claude agent for editing the question bank (add/remove questions) is the next feature to build

## Constraints

- **Platform**: n8n (self-hosted or cloud) — workflow must use n8n node types
- **Email**: Gmail via OAuth
- **Sheet**: Google Sheets — single Bank tab
- **No AI in workflow**: Workflow is static logic only; Claude is not called at runtime

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Single workflow (not A + B) | Simpler — no timing dependency between two workflows | ✓ Good |
| Direct from bank, no queue buffer | 130 questions is a large enough buffer; no top-up logic needed | ✓ Good |
| One Bank tab (no Domains tab) | Domain is row-level metadata; Domains tab only served AI rotation logic | ✓ Good |
| Read all rows, filter in Code node | n8n `filtersUI` only returns first matching row — filtering in Code node is more reliable | ✓ Good |
| VPS hosting | Workflow only runs when local machine is on — needs always-on host for reliable 06:30 delivery | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-15 — Milestone v1.1 Deploy started*
