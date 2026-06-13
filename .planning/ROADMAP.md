# Roadmap: Daily Learning — n8n Email Workflow

## Overview

Two phases of work: first restructure the Google Sheet into a single Bank tab seeded with all 130 questions, then build the n8n workflow that reads from it, composes a plain-text email with 3 questions, sends via Gmail, and marks those questions sent. When both phases are complete, a question lands in the inbox every morning automatically.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Sheet Setup** - Create and seed the Bank tab with all 130 questions
- [x] **Phase 2: Workflow** - Build n8n workflow that picks, emails, and marks 3 questions daily
- [x] **Phase 3: Curator Agent** - Claude-powered skill+agent that edits the question bank via natural language and syncs to the Google Sheet (completed 2026-06-13)

## Phase Details

### Phase 1: Sheet Setup
**Goal**: The Google Sheet has a single Bank tab, correctly structured and seeded with all 130 questions ready to send
**Depends on**: Nothing (first phase)
**Requirements**: SHEET-01, SHEET-02
**Success Criteria** (what must be TRUE):
  1. Bank tab exists with exactly five columns: question, domain, est_minutes, status, date_sent
  2. All 130 questions from questions.md are present in the Bank tab with status = queued
  3. No other data tabs interfere — sheet has one clear Bank tab as the data source
**Plans**: TBD

### Phase 2: Workflow
**Goal**: A single n8n workflow runs every morning at 06:30, picks the 3 oldest queued questions, emails them, and marks them sent
**Depends on**: Phase 1
**Requirements**: WF-01, WF-02, WF-03, WF-04, WF-05
**Success Criteria** (what must be TRUE):
  1. Workflow triggers automatically at 06:30 daily without manual intervention
  2. Exactly 3 questions appear in the inbox email, in row order (oldest queued first), with no answers or hints
  3. Each emailed question shows domain and est_minutes alongside the question text in plain text
  4. After sending, those 3 rows in the Bank tab show status = sent and today's date in date_sent
  5. Running the workflow a second time on the same day picks the next 3 queued questions, not the already-sent ones
**Plans**: TBD

### Phase 3: Curator Agent
**Goal**: A Claude-powered agent the user can invoke with natural language to add, remove, or refine questions in the bank — writes to questions.md and syncs new rows to the Google Sheet Bank tab
**Depends on**: Phase 1, Phase 2
**Requirements**: FUTURE-01
**Success Criteria** (what must be TRUE):
  1. User can invoke the agent with a loose instruction ("add 5 volcano questions") and get correctly formatted questions added to questions.md
  2. New questions follow the daily-question-curator quality bar (specific, non-obvious, spoiler-free)
  3. New questions are also appended to the Google Sheet Bank tab with status = queued
  4. Removals by name or description are reflected in both questions.md and the sheet
  5. No duplicate questions are introduced
**Plans**: 3 plans
- [x] 03-01-PLAN.md — Repo foundations (.gitignore, .secrets/) and Python Sheets API helper script
- [x] 03-02-PLAN.md — Service account credential drop-in and live Bank tab verification
- [x] 03-03-PLAN.md — /curate-bank SKILL.md with preview gates and end-to-end add/remove verification

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Sheet Setup | 1/1 | Complete | 2026-06-13 |
| 2. Workflow | 1/1 | Complete | 2026-06-13 |
| 3. Curator Agent | 3/3 | Complete   | 2026-06-13 |
