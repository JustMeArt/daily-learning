# Phase 3: Curator Agent - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-13
**Phase:** 3-Curator Agent
**Areas discussed:** Sheet sync, Source of truth, Removal handling, Agent trigger

---

## Sheet Sync

| Option | Description | Selected |
|--------|-------------|----------|
| n8n webhook | Create a small n8n endpoint that accepts questions as JSON and appends them to the Bank tab | |
| Direct Sheets API | Agent calls Google Sheets API directly — needs OAuth token handling outside n8n | ✓ |
| Manual sync | Agent only writes to questions.md; user re-runs the seeder when they want the sheet updated | |

**User's choice:** Direct Sheets API

| Auth Option | Description | Selected |
|-------------|-------------|----------|
| Service Account | Download JSON key from Google Cloud, share sheet with service account email — one-time setup | ✓ |
| Reuse n8n OAuth token | Extract from n8n — tricky, tokens expire | |
| You decide | Leave auth approach to the planner | |

**User's choice:** Service Account

| Key location | Description | Selected |
|--------------|-------------|----------|
| Project directory (.secrets/) | Kept with the project, added to .gitignore | ✓ |
| Home directory (~/.config/) | Shared across projects, not tied to this repo | |
| You decide | Planner picks the location | |

**User's choice:** `.secrets/` in project directory

---

## Source of Truth

| Option | Description | Selected |
|--------|-------------|----------|
| questions.md | File is the truth — agent writes here first, then syncs to sheet | ✓ |
| Google Sheet | Sheet is the truth — agent writes directly there | |
| Both equally | Always kept perfectly in sync — adds complexity | |

**User's choice:** questions.md

| Divergence handling | Description | Selected |
|--------------------|-------------|----------|
| questions.md wins, always | Agent only reads questions.md — sheet divergence is user's problem | |
| Agent warns you | Agent detects mismatch and flags it before writing | ✓ |
| Ignore it | Don't worry about divergence | |

**User's choice:** Agent warns on divergence before writing

---

## Removal Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Mark as removed | Set status = 'removed' in sheet — daily workflow skips it | |
| Delete the row | Row is gone from the sheet entirely | ✓ |
| Leave it | Question stays queued in sheet and will still get sent | |

**User's choice:** Delete the row (corrected after initial misclick on "Leave it")

| Identification | Description | Selected |
|----------------|-------------|----------|
| Describe loosely | "remove the onion one" — Claude finds the best match | |
| Exact question text | Paste the full question text | |
| Both | Loose description when obvious, exact text when multiple close matches | ✓ |

**User's choice:** Both — loose or direct, Claude resolves

---

## Agent Trigger

| Option | Description | Selected |
|--------|-------------|----------|
| New skill wrapping existing one | /curate-bank uses daily-question-curator logic internally, then writes | ✓ |
| Extend existing skill | Add file-writing directly into daily-question-curator | |
| Separate script | Python script run from terminal | |

**User's choice:** New `/curate-bank` skill

| Invocation style | Description | Selected |
|-----------------|-------------|----------|
| Inline only | /curate-bank add 5 volcano questions | |
| Interactive only | Invoke then it asks what you want | |
| Either works | Inline if you know, interactive if you don't | ✓ |

**User's choice:** Either works — flexible invocation

| Write behavior | Description | Selected |
|----------------|-------------|----------|
| Preview first | Shows questions/removals, user approves, then writes | ✓ |
| Execute and confirm | Writes immediately, shows what it did | |
| You decide | Claude judges based on action | |

**User's choice:** Preview first, then write on approval

---

## Claude's Discretion

- Exact format of the preview (table, list, inline)
- How to handle ambiguous removal matches (multiple close candidates)

## Deferred Ideas

- VPS hosting for n8n — already logged in PROJECT.md
- Automatic bank top-up when questions run low — future Phase 4
- Web UI or Telegram bot for remote invocation — future phase
