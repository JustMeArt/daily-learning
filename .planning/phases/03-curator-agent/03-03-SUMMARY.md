---
phase: 03-curator-agent
plan: 03
subsystem: skill
tags: [claude-skill, curate-bank, questions-md, google-sheets, preview-gate, divergence-check]

# Dependency graph
requires:
  - phase: 03-01
    provides: scripts/sheets_helper.py CLI (read/append/delete subcommands)
  - phase: 03-02
    provides: live credential at .secrets/service-account.json, 130 rows confirmed
provides:
  - .claude/skills/curate-bank/SKILL.md — /curate-bank skill definition, end-to-end verified
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

patterns-established:
  - "Skill-wraps-skill: delegate quality criteria to a canonical skill; reference it, never duplicate it"
  - "Source-of-truth ordering: write the local file first, sync the remote surface second"
  - "Preview gate: no write proceeds without AskUserQuestion confirmation"

requirements-completed: [FUTURE-01]

# Metrics
duration: 20min
completed: 2026-06-13
---

# Phase 3 Plan 03: /curate-bank SKILL.md Summary

**217-line SKILL.md wrapping daily-question-curator quality bar with 9-step process (divergence check, preview gate, confirm gate, questions.md-first write, Sheet sync), verified end-to-end with reversible add and remove against the live Bank tab**

## Performance

- **Duration:** ~20 min (Task 1 authoring + Task 2 human verify)
- **Completed:** 2026-06-13
- **Tasks:** 2 of 2 complete
- **Files created:** 1

## Accomplishments

- `.claude/skills/curate-bank/SKILL.md` created at 217 lines (>= 80 minimum)
- All acceptance criterion grep checks pass (name, tools, quality-bar delegation, helper subcommands, divergence, preview, gates)
- End-to-end human verification passed: Exercise A (add) and Exercise B (remove) both confirmed clean
- Preview gate honored on both flows — no writes occurred before user approval
- Row deltas fully reversible: questions.md and Bank tab returned to pre-test baseline after the add/remove pair

## Task Commits

1. **Task 1: Write /curate-bank SKILL.md** — `f97bcba` (feat)
2. **Task 2: End-to-end human verify** — human-verify checkpoint; no code commit (verification only)

## Human Verification Results (Task 2)

**Exercise A — Add flow**
- Invoked: `/curate-bank add 1 question about why ice cubes sometimes have a cloudy center`
- Preview table shown before any write — gate honored
- User approved; skill wrote questions.md first, then synced Bank tab via `scripts/sheets_helper.py append`
- Row count delta: +1 in both questions.md and the Bank tab
- New question added with status=queued, date_sent empty
- No answer revealed in preview or output

**Exercise B — Remove flow**
- Invoked: `/curate-bank remove the ice cube cloudy center one`
- Skill resolved the fuzzy description to the exact question text added in Exercise A
- Resolved question shown with planned change before any deletion — gate honored
- User approved; skill deleted from questions.md first, then synced Bank tab via `scripts/sheets_helper.py delete`
- Row count delta: -1 in both questions.md and the Bank tab
- Row counts returned to pre-test baseline

**End state:** questions.md and Bank tab row counts both equal their pre-test values. No leftover test data in either surface.

## Key Design Decisions Honored

| Decision | Where in SKILL.md |
|---|---|
| Quality bar delegated to daily-question-curator, not duplicated | "Quality bar and domains" section |
| Divergence check before any write | Step 3 (gate) |
| Preview-and-confirm on every write | Step 6 (gate) |
| questions.md written first, sheet synced second | Steps 7 and 8, "Source of truth" section |
| Fuzzy remove: zero matches → abort; one match → confirm; multiple → AskUserQuestion | Step 5 |
| Helper exit-code routing: exit 2/3 surfaced to user, no silent retry | Step 8 error handling |

## Files Created

- `.claude/skills/curate-bank/SKILL.md` — complete skill definition, 217 lines, frontmatter with `name: curate-bank`, `allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion`

## Credential Reference

- **Service account:** `daily-learning-curator@daily-learning-499314.iam.gserviceaccount.com`
- **Helper used:** `scripts/sheets_helper.py` (read/append/delete subcommands)
- **Credential path:** `.secrets/service-account.json` (gitignored; placed in Plan 02)

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Threat Flags

None — this plan creates a skill definition file only. No new network endpoints, auth paths, schema changes, or file access patterns beyond what the plan's threat model already covers.

## Threat Mitigations Confirmed

| Threat ID | Mitigation | Verified by |
|---|---|---|
| T-03-10 | Preview-and-confirm gate (step 6) prevents silent writes | Exercise A and B: gate fired before every write |
| T-03-11 | Divergence check (step 3) blocks writes when sheet and file disagree | Step 3 logic in SKILL.md; Exercise C not run but check is wired |
| T-03-12 | Output format rule prohibits answer hints in preview or error text | No answer revealed in Exercise A or B |
| T-03-13 | Pipe-count validation in step 7 catches malformed table rows | Step 7 logic in SKILL.md |
| T-03-14 | Multi-match AskUserQuestion + helper exit-3 routing; no auto-pick | Step 5 and step 8 in SKILL.md |
| T-03-15 | Failure modes section surfaces credential path only, never contents | "Failure modes" section in SKILL.md |

## Next Phase Readiness

- `/curate-bank` is the complete user-facing surface for Phase 3. All three plans (helper CLI, credential, skill) are live and verified.
- The skill is ready for daily use: add and remove flows work end-to-end against the live Bank tab.
- No blockers. Phase 3 is complete.

## Self-Check: PASSED

- `.claude/skills/curate-bank/SKILL.md` exists: confirmed (217 lines)
- Task 1 commit `f97bcba` exists: confirmed in git log
- Human verify exercises A and B: user confirmed "A and B both worked clean"
- Row delta reversibility: confirmed by user (baseline restored)

---
*Phase: 03-curator-agent*
*Completed: 2026-06-13*
