# Phase 3: Curator Agent - Context

**Gathered:** 2026-06-13
**Status:** Ready for planning

<domain>
## Phase Boundary

A Claude-powered skill (`/curate-bank`) the user invokes with natural language to add or remove questions in the bank. The skill uses the existing `daily-question-curator` quality logic, writes changes to `questions.md`, and syncs additions/deletions to the Google Sheet Bank tab via the Sheets API directly (service account auth). Questions.md is the source of truth; the sheet is a derived delivery mechanism.

</domain>

<decisions>
## Implementation Decisions

### Sheet Sync
- **D-01:** Agent calls Google Sheets API directly — no n8n dependency at runtime
- **D-02:** Authentication via Service Account (JSON key file) — one-time setup, no token expiry issues
- **D-03:** Service account key stored in `.secrets/` within the project directory (add to `.gitignore`)

### Source of Truth
- **D-04:** `questions.md` is the authoritative source — agent writes here first, then syncs to sheet
- **D-05:** If sheet and `questions.md` diverge (e.g. user edits sheet manually), agent warns before writing — does not silently overwrite

### Removal Handling
- **D-06:** Removals delete the row from `questions.md` AND delete the matching row from the Google Sheet
- **D-07:** User identifies questions to remove loosely ("the onion one") or directly (exact text) — Claude finds the best match

### Agent Trigger
- **D-08:** New skill `/curate-bank` that wraps `daily-question-curator` logic — keeps existing skill unchanged
- **D-09:** Supports both inline (`/curate-bank add 5 volcano questions`) and interactive (invoke then describe) invocation
- **D-10:** Preview-first — shows generated questions / planned removals before writing anything; user approves before changes land

### Claude's Discretion
- Exact format of the preview (table, list, etc.) — match the `daily-question-curator` output style
- How to handle ambiguous removal matches (multiple close candidates) — show options, ask user to confirm

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Question Bank
- `questions.md` — merged question bank (130 questions, markdown table: question | domain | est_minutes); source of truth
- `question-bank.md` — original 80 questions (8 domains × 10)
- `question-bank-science.md` — science-domain 50 questions (5 domains × 10)

### Skill to Reuse
- `.claude/skills/daily-question-curator/` — existing curator skill; Phase 3 wraps this logic, does NOT modify it. Read SKILL.md for quality bar, domain list, add/remove/refine/review actions, and output format.

### Google Sheet
- Sheet ID: `16zTv6lo9SXhZdcorvfhieB46wzbVDwNTDZCpriJdNlE`
- Tab name: `Bank`
- Columns: question, domain, est_minutes, status, date_sent
- New rows appended with `status = queued`, `date_sent = ""`
- Deletions match on `question` column text (exact match after Claude resolves loose description)

### Planning Docs
- `.planning/PROJECT.md` — project constraints and key decisions
- `.planning/REQUIREMENTS.md` — FUTURE-01 is the requirement this phase implements

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `daily-question-curator` skill: quality bar, domain list, spoiler-free rule, add/remove/refine/review logic, and table output format — use as-is, don't duplicate
- n8n Google Sheets credential (`VtxlcZP53fH6sIo6`) — NOT used here (service account replaces it for the agent)

### Established Patterns
- `questions.md` markdown table format: `| question | domain | est_minutes |` — new questions must match this format exactly
- Bank tab row format: question, domain, est_minutes, status=queued, date_sent="" — append-only for additions
- Removal by question text match — same pattern used in the n8n `Mark Sent` node

### Integration Points
- `/curate-bank` writes to `questions.md` (file write) and Google Sheet (Sheets API via service account)
- Daily n8n workflow (`WT359GdOyEqgHsma`) reads the Bank tab independently — agent changes are automatically picked up next run

</code_context>

<specifics>
## Specific Ideas

- The `daily-question-curator` skill already defines the exact output format (markdown table). The new skill should reuse this format for its preview step.
- Service account setup mirrors the Google OAuth setup done for n8n — same Google Cloud project can be reused, just add a Service Account credential.
- Loose removal matching: "the onion one" → Claude identifies "Why does cutting an onion make you cry?" → shows it → user confirms → deletes.

</specifics>

<deferred>
## Deferred Ideas

- VPS hosting for n8n (already logged in PROJECT.md as Active requirement)
- Automatic bank top-up when questions run low (would be a Phase 4)
- Web UI or Telegram bot for invoking the curator remotely

</deferred>

---

*Phase: 3-Curator Agent*
*Context gathered: 2026-06-13*
