---
phase: 03-curator-agent
plan: 03
subsystem: skill
tags: [claude-skill, curate-bank, questions-md, google-sheets, preview-gate, divergence-check]

# Dependency graph
requires:
  - phase: 03-01
    provides: scripts/sheets_helper.py CLI (read/append/delete)
  - phase: 03-02
    provides: live credential at .secrets/service-account.json, 130 rows confirmed
provides:
  - .claude/skills/curate-bank/SKILL.md — /curate-bank skill definition
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Skill wraps an existing skill (daily-question-curator) without duplicating its quality bar
    - Preview-and-confirm gate via AskUserQuestion before any write
    - Divergence check (read sheet, compare to file) before any write
    - questions.md written first; sheet sync second (source of truth ordering)
    - Fuzzy removal with multi-candidate AskUserQuestion gate (no silent auto-selection)
    - Helper exit-code routing: exit 2/3 surfaced to user, no silent retry

key-files:
  created:
    - .claude/skills/curate-bank/SKILL.md
  modified: []

key-decisions:
  - "Quality bar delegated entirely to daily-question-curator SKILL.md — not duplicated here (D-08)"
  - "questions.md is source of truth; sheet is derived delivery surface (D-04)"
  - "Divergence warning gate in step 3 blocks all writes until user acknowledges (D-05)"
  - "Fuzzy removal never auto-picks on ambiguity — always asks via AskUserQuestion (D-07)"
  - "Preview-and-confirm gate is step 6 — mandatory, cannot be skipped (D-10)"
  - "est_minutes constrained to 15, 30, or 60 only"
  - "Domain casing mirrors questions.md exactly (13 domains listed in step 4)"

# Metrics
duration: 5min
completed: 2026-06-13
---

# Phase 3 Plan 03: /curate-bank SKILL.md Summary

**217-line SKILL.md wrapping daily-question-curator quality bar with 9-step process: divergence check, preview gate, confirm gate, questions.md-first write, and Google Sheet sync via sheets_helper.py**

## Status

- **Task 1 (Write SKILL.md):** COMPLETE — committed `f97bcba`
- **Task 2 (End-to-end human verify):** PENDING — checkpoint awaits user exercise of add and remove flows

## Performance

- **Duration:** ~5 min
- **Completed:** 2026-06-13
- **Tasks:** 1 of 2 completed (Task 2 is a human-verify checkpoint)
- **Files created:** 1

## Accomplishments

- `.claude/skills/curate-bank/SKILL.md` created at 217 lines (>= 80 minimum)
- All acceptance criterion grep checks pass:
  - `name: curate-bank` in frontmatter
  - `daily-question-curator` referenced (quality bar delegated, not duplicated)
  - `sheets_helper.py` referenced with all three subcommands: `read`, `append`, `delete`
  - `questions.md` referenced as source of truth
  - `divergence`, `preview`, `AskUserQuestion` present in body
  - `Parse intent` and `Sync Google Sheet` present in flow line
  - No forbidden phrases: `SPOILER-FREE` and `Hiding a NON-OBVIOUS` absent
- All 9 process steps from PLAN.md spec wired in, in order
- All 6 STRIDE threat mitigations from plan threat_model addressed:
  - T-03-10: preview-and-confirm gate in step 6
  - T-03-11: divergence check in step 3
  - T-03-12: output format rule prohibits answer hints
  - T-03-13: pipe-count validation in step 7
  - T-03-14: multi-match AskUserQuestion in step 5; helper exit-3 routing in step 8
  - T-03-15: failure modes section surfaces credential path only, never contents

## Task Commits

1. **Task 1: Write /curate-bank SKILL.md** — `f97bcba` (feat)

## Files Created

- `.claude/skills/curate-bank/SKILL.md` — complete skill definition, 217 lines

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — the SKILL.md is fully specified. Task 2 (human verify) will confirm the skill works
end-to-end against the live bank.

## Threat Flags

None — this plan creates a skill definition file only (no new network endpoints, no new auth
paths, no schema changes beyond what the plan's threat model already covers).

## Pending: Task 2 Human Verify

The orchestrator will handle Task 2 separately. The user must exercise:

- **Exercise A:** `/curate-bank add 1 question about why ice cubes sometimes have a cloudy center`
  — confirm preview before write, approve, verify row count delta +1 in both questions.md and the
  Bank tab, no answer revealed.

- **Exercise B:** `/curate-bank remove the ice cube cloudy center one`
  — confirm resolved question shown before delete, approve, verify row count delta -1, question
  fully removed from both surfaces.

- **Exercise C (recommended):** Manually add a stray row to the Bank tab, invoke
  `/curate-bank add ...`, confirm divergence warning fires before any write, abort.

Resume signal: "approved — A and B passed" (and optionally "C passed").

---
*Phase: 03-curator-agent*
*Completed: 2026-06-13 (Task 1 only; Task 2 checkpoint pending)*
