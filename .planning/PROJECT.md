# Daily Learning — n8n Email Workflow

## What This Is

A single n8n workflow that sends 3 curiosity questions by email every morning at 06:30. Questions are drawn from a static bank of 130 hand-curated questions stored in a Google Sheet. The workflow picks the 3 oldest unsent questions, emails them via Gmail, and marks them sent.

## Core Value

A question lands in the inbox every morning — no setup friction, no AI dependency, no gaps.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Google Sheet has a single `Bank` tab with columns: question, domain, est_minutes, status, date_sent
- [ ] Bank tab seeded with all 130 questions from questions.md (status = queued)
- [ ] Single n8n workflow triggers daily at 06:30
- [ ] Workflow reads Bank tab, filters status = queued, picks 3 oldest
- [ ] Workflow sends those 3 questions via Gmail
- [ ] Workflow marks each sent question: status = sent, date_sent = today
- [ ] Email is plain text, no answers, no hints — just the questions with domain and est_minutes

### Out of Scope

- AI question generation — no Claude API calls in the workflow (future Claude agent handles bank edits)
- Domains tab — domain lives on the question row, no separate tab needed
- Queue depth top-up logic — bank is pre-seeded, no Workflow A equivalent

## Context

- Existing Google Sheet has Queue + Domains tabs — needs restructuring to single Bank tab
- questions.md contains 130 questions in a markdown table (question, domain, est_minutes)
- n8n instance is accessible via API — workflow can be created directly
- Gmail will be used for sending via OAuth in n8n
- A future Claude agent (separate project) will handle adding/removing questions from the bank

## Constraints

- **Platform**: n8n (self-hosted or cloud) — workflow must use n8n node types
- **Email**: Gmail via OAuth
- **Sheet**: Google Sheets — single Bank tab
- **No AI in workflow**: Workflow is static logic only; Claude is not called at runtime

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Single workflow (not A + B) | Simpler — no timing dependency between two workflows | — Pending |
| Direct from bank, no queue buffer | 130 questions is a large enough buffer; no top-up logic needed | — Pending |
| One Bank tab (no Domains tab) | Domain is row-level metadata; Domains tab only served AI rotation logic | — Pending |

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
*Last updated: 2026-06-13 after initialization*
