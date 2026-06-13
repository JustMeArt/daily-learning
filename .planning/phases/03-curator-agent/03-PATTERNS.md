# Phase 3: Curator Agent - Pattern Map

**Mapped:** 2026-06-13
**Files analyzed:** 3 new/modified files
**Analogs found:** 3 / 3

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `.claude/skills/curate-bank/SKILL.md` | skill (wrapper) | request-response + file-I/O | `/home/lennart/.claude/skills/daily-question-curator/SKILL.md` | exact role, wraps that skill |
| `questions.md` | data file | file-I/O (append + delete rows) | existing `questions.md` (130-question markdown table) | self-analog — extend in place |
| `.secrets/service-account.json` | config/secret | none (static credential) | no analog (new pattern for this project) | none |

---

## Pattern Assignments

### `.claude/skills/curate-bank/SKILL.md` (skill-wrapper, request-response + file-I/O)

**Analog:** `/home/lennart/.claude/skills/daily-question-curator/SKILL.md`
**Secondary analogs (SKILL.md structure):** `gsd-capture/SKILL.md`, `gsd-inbox/SKILL.md`

**Frontmatter pattern** (daily-question-curator SKILL.md lines 1-6):
```yaml
---
name: daily-question-curator
description: Curate the daily-learning question list — add, remove, refine, or review everyday-curiosity questions and their domains. Use when the user shares a thought about a topic to add, something to remove, asks to review domain balance, or wants new questions generated for a specific domain.
---
```
Copy this structure exactly for `curate-bank`. Use `name: curate-bank`. The `description:` should cover "add or remove questions in the bank, syncing questions.md and the Google Sheet."

**Allowed-tools pattern** (gsd-capture SKILL.md lines 7-13):
```yaml
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
```
`curate-bank` needs all of these. `Bash` is required for calling the Sheets API (via `curl` or a helper script). `AskUserQuestion` is needed for the preview-and-confirm flow and ambiguous match resolution.

**Argument-hint pattern** (gsd-capture SKILL.md line 9):
```yaml
argument-hint: "[--note | --backlog | --seed | --list] [text]"
```
For `curate-bank`, use:
```yaml
argument-hint: "[add <description>] [remove <description>]"
```

**Inline `<objective>` block** (gsd-inbox SKILL.md lines 14-22):
```
<objective>
One-command triage of the project's GitHub inbox. Fetches all open issues and PRs,
reviews each against the corresponding template requirements ...

**Flow:** Detect repo → Fetch open issues + PRs → Classify each by type → Review against template → Report findings → Optionally act (label, comment, close)
</objective>
```
Copy this pattern. Summarize the skill's purpose and state the linear flow explicitly:
```
**Flow:** Parse intent → Generate/identify questions → Preview → User approves → Write questions.md → Sync Google Sheet
```

**`<context>` block with $ARGUMENTS** (gsd-capture SKILL.md lines 48-57):
```
<context>
Arguments: $ARGUMENTS

Parse the first token of $ARGUMENTS:
- If it is `--note`: strip the flag, pass remainder to note workflow
...
</context>
```
For `curate-bank`, route on first token:
- `add` → generation flow using `daily-question-curator` quality bar
- `remove` → fuzzy-match + confirm flow
- (no args) → interactive: ask what the user wants to do

**`<process>` block** (gsd-capture SKILL.md lines 59-63):
```
<process>
1. Parse the leading flag (if any) from $ARGUMENTS.
2. Load and execute the appropriate workflow end-to-end based on the routing table above.
3. Preserve all workflow gates from the target workflow.
</process>
```
`curate-bank`'s process block should enumerate all mandatory gates: quality bar check, duplicate check, preview step, user confirmation, `questions.md` write, Sheet sync, divergence warning.

**Quality bar and domains — copy verbatim from analog** (daily-question-curator SKILL.md lines 13-30):
```
## The bar — every question must be
- About something ORDINARY the person meets in normal life ...
- Hiding a NON-OBVIOUS but findable "huh, I never thought about that" beneath it.
- SPECIFIC and concrete ...
- Answerable in one sitting from a single decent web page.
- Not already obvious to most adults ...
- SPOILER-FREE. The question must never reveal or hint at its own answer.
  This rule is absolute — a spoiled question is worthless.

## Domains (current)
kitchen & food | the body | household objects & built environment |
...
```
Do NOT duplicate this in `curate-bank` — instead, reference it: "Quality bar and domain list defined in `daily-question-curator` SKILL.md — apply exactly as stated there."

**Output format — copy from analog** (daily-question-curator SKILL.md lines 57-61):
```
Return additions as a ready-to-paste table:
| question | domain | est_minutes |

Confirm removals explicitly. Show refined questions as before → after.
Never include the answer to any question, even as a hint.
```
The preview step should use this exact table format before any writes.

---

### `questions.md` (data file, file-I/O — append rows / delete rows)

**Analog:** existing `questions.md` (self-analog — extend the file, do not reformat it)

**Exact header and separator pattern** (questions.md lines 3-4):
```markdown
| question | domain | est_minutes |
|---|---|---|
```
All added rows must use pipe-delimited format with no trailing spaces. The three columns are `question`, `domain`, `est_minutes` — in that order, matching the Bank tab column order exactly.

**Row format pattern** (questions.md lines 5-14, representative sample):
```markdown
| Why do recipes tell you to preheat the oven instead of just turning it on when the food goes in? | Kitchen & food | 15 |
| Why does bread go stale faster in the fridge than on the counter? | Kitchen & food | 15 |
```
Key constraints extracted from the existing rows:
- Domain names use title case: `Kitchen & food`, `The body`, `Household objects & built environment`, etc.
- `est_minutes` values are always one of: `15`, `30`, `60`
- Questions end with `?`
- No internal pipe characters in question text

**Append pattern:** New rows go at the end of the file, after the last existing row. Do not renumber or reorder existing rows.

**Delete pattern:** When removing, find the row matching the resolved question text exactly, remove that single line. No blank lines left behind.

**Bank tab column mapping** (from CONTEXT.md canonical refs):
- Sheet columns: `question | domain | est_minutes | status | date_sent`
- `questions.md` columns map to the first three; `status = queued` and `date_sent = ""` are set by the agent only when writing to the Sheet, not stored in `questions.md`.

---

### `.secrets/service-account.json` (config/secret, static credential)

**No close analog in this project.** The pattern is standard Google Service Account JSON — the file is created by downloading from Google Cloud Console, not generated by code.

**Setup pattern** (from sheet-setup.md lines 53-63 — the OAuth pattern already established):
```
In n8n, the Google Sheets node authenticates via OAuth2 or a Service Account.
Whichever you use, make sure the Google account (or service account email) has
Editor access to this sheet.
```
The service account credential follows the same Google Cloud project as the existing n8n OAuth. The agent reads this file at runtime using `Bash` (e.g., `cat .secrets/service-account.json` to extract the private key for a JWT, or pass the file path to a helper script).

**`.gitignore` pattern:** `.secrets/` must be added to `.gitignore`. No existing `.gitignore` exists in this project — one must be created as part of this phase.

---

## Shared Patterns

### Preview-Before-Write Gate
**Source:** CONTEXT.md decision D-10 + daily-question-curator output format (SKILL.md lines 57-61)
**Apply to:** All write operations in `curate-bank`

Pattern to implement:
1. Show proposed changes in the standard table format
2. Explicitly ask for confirmation before any file or sheet writes
3. Only proceed if user approves — abort cleanly if not

For additions, preview = the generated question table.
For removals, preview = the resolved question text + "will delete this from questions.md and the Bank tab."

### Divergence Warning Gate
**Source:** CONTEXT.md decision D-05
**Apply to:** All write operations that touch the Google Sheet

Before writing to the Sheet, compare the question texts currently in `questions.md` against the rows in the Bank tab (via Sheets API read). If they differ:
- Report the discrepancy clearly (what is in questions.md but not the sheet, and vice versa)
- Do not proceed with the write until the user acknowledges or resolves the divergence

### Ambiguous Match Resolution
**Source:** CONTEXT.md decision D-07 + daily-question-curator SKILL.md "Remove" action (lines 43-47)
**Apply to:** Remove operations in `curate-bank`

Pattern from analog:
```
Remove: Cull questions that are too obvious, too broad, unanswerable from one page,
duplicated, or self-spoiling. When removing for being "too obvious," say briefly
why — so the user can overrule if they disagree.
```
Extension for `curate-bank`: when the user's loose description matches multiple questions, list all candidates (with full question text), ask the user to confirm the right one before proceeding. Never guess silently.

### Google Sheets API Auth Pattern
**Source:** No existing analog — new to this project
**Apply to:** All Sheets API calls in `curate-bank`

The skill calls the Sheets API via `Bash` using either:
- A helper Python/Node script that reads `.secrets/service-account.json` and uses the Google API client library, or
- Direct `curl` with a JWT bearer token generated from the service account key

Sheet ID: `16zTv6lo9SXhZdcorvfhieB46wzbVDwNTDZCpriJdNlE`
Tab name: `Bank`
Operations needed:
- **Read all rows** (to check divergence and find question to delete)
- **Append row** with `status = queued`, `date_sent = ""`
- **Delete row by question text match** (find row index, then delete)

The planner should decide whether to use a Python helper script (simpler auth via `google-auth` library) or raw curl (no library dependency). Prefer the library approach — it handles JWT signing automatically.

### Questions.md Table Format
**Source:** `questions.md` lines 1-14 (self-analog)
**Apply to:** All additions to questions.md

```markdown
| question | domain | est_minutes |
|---|---|---|
| <question text ending in ?> | <Domain Title Case> | <15|30|60> |
```
The file must remain a valid markdown table after every edit. Validate that pipe counts match on every row before writing.

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `.secrets/service-account.json` | config/secret | none | No service account credentials exist in this project yet — created by user via Google Cloud Console |
| `.gitignore` | config | none | No `.gitignore` exists in this project yet — needs to be created to exclude `.secrets/` |

---

## Metadata

**Analog search scope:** `/home/lennart/.claude/skills/` (all SKILL.md files), `/home/lennart/Projects/jcma/daily-learning/` (all project files)
**Files scanned:** 8 (daily-question-curator SKILL.md, gsd-capture SKILL.md, gsd-inbox SKILL.md, gsd-docs-update SKILL.md, gsd-import SKILL.md, questions.md, sheet-setup.md, n8n-workflow-a.md)
**Pattern extraction date:** 2026-06-13
