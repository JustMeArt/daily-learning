---
name: curate-bank
description: Add or remove questions in the daily-learning bank using natural language. Wraps the daily-question-curator quality bar; writes to questions.md and syncs the change to the Google Sheet Bank tab via scripts/sheets_helper.py. Use when the user wants to add new questions, remove existing ones, or refine the bank.
argument-hint: "[add <description>] [remove <description>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Curate the daily-learning question bank

<objective>
This skill is the user-facing surface for editing the daily-learning question bank. It accepts a
loose natural-language intent (add some questions about a topic, remove a question that is not
working, refine the set), applies the quality bar from the `daily-question-curator` skill, writes
the change to `questions.md` as the source of truth, and then syncs the change to the Google
Sheet Bank tab via `scripts/sheets_helper.py`. Every write is gated by a preview-and-confirm
step — nothing is written until the user explicitly approves.

**Flow:** Parse intent → Generate or identify questions → Preview → User approves → Write questions.md → Sync Google Sheet
</objective>

## Quality bar and domains

Quality bar and domain list are defined in `~/.claude/skills/daily-question-curator/SKILL.md`
(sections "The bar" and "Domains (current)"). Apply them exactly as stated there.

When adding to a brand-new domain, generate 8–10 starters per the analog's Add action — a
single question is not enough to anchor a new domain.

Do not reproduce or paraphrase the bar rules here. Delegate entirely to the analog skill.

<context>
Arguments: $ARGUMENTS

Parse the first token of $ARGUMENTS:

- First token is `add` — strip the flag, treat the remainder as the loose add description; route
  to the Add flow (steps 4, 6–9 below).

- First token is `remove` — strip the flag, treat the remainder as the loose removal description;
  route to the Remove flow (steps 5, 6–9 below).

- No arguments, or first token is neither `add` nor `remove` — ask interactively: use
  AskUserQuestion to ask "Do you want to add or remove questions?" and then "Describe what you
  want to add or remove." Proceed with the supplied intent as if it had been provided inline.
</context>

<process>
Execute every step in order. Do not skip or reorder. Steps marked as gates must complete with
explicit user confirmation before continuing.

**Step 1 — Parse intent.**
Extract the leading flag (`add` or `remove`) from $ARGUMENTS. If absent, use AskUserQuestion to
collect it interactively. Record the direction and the loose description that follows the flag.

**Step 2 — Load questions.md into memory.**
Read `questions.md` from the repo root. Parse every data row (rows after the two-line header)
into a list of `{ question, domain, est_minutes }` records. This list is used for duplicate
detection (Add flow) and fuzzy matching (Remove flow).

**Step 3 — Divergence check (gate).**
Run `python scripts/sheets_helper.py read` from the repo root. Parse the JSON array it emits to
stdout. Extract the set of question texts from the sheet. Compare that set against the set of
question texts in questions.md.

If the two sets differ:
- Compute and display two lists: (a) questions in questions.md but not in the sheet, (b)
  questions in the sheet but not in questions.md.
- Use AskUserQuestion to ask: "questions.md and the Bank tab are out of sync. How do you want to
  proceed? (a) continue anyway, (b) abort, (c) treat questions.md as truth and re-sync after the
  change."
- Do NOT silently overwrite or ignore the divergence.
- Only proceed with the chosen intent after the user has acknowledged the state.

If the sets match, continue to step 4 or 5.

**Step 4 — Add flow: generate candidate questions.**
Apply the quality bar from `daily-question-curator` SKILL.md to generate N candidate questions
matching the user's description and chosen domain(s). For each candidate:
- Check for duplicates against the questions.md list using case-insensitive full-text and
  near-duplicate review; drop any that are too similar to an existing question.
- Assign one of the 13 existing domains, using the exact title-casing from questions.md (e.g.
  `Kitchen & food`, `The body`, `Household objects & built environment`,
  `Social customs & language`, `Money & everyday systems`,
  `Nature, weather & everyday science`, `Everyday tech`, `Games & puzzles`,
  `Medicine & health`, `Biology & the living world`, `Earth & geology`, `Math & numbers`,
  `Space & sky`). If the user describes a brand-new domain, generate 8–10 starters for it.
- Assign est_minutes: only `15`, `30`, or `60`.
- Emit a preview table listing all candidates:

  | question | domain | est_minutes |
  |---|---|---|
  | <question text> | <Domain Title Case> | <15|30|60> |

Proceed to step 6 (preview-and-confirm gate).

**Step 5 — Remove flow: resolve the target question.**
Perform a full-text fuzzy match of the user's loose description against the question text of
every row in questions.md.

- Zero matches: tell the user "No matching question found" with the description used, and abort.
  Do not write anything.
- Exactly one match: display the resolved question text and note "Will delete this row from
  questions.md and the Bank tab." Proceed to step 6.
- Multiple plausible matches: list all candidates with their full question text and domain. Use
  AskUserQuestion to ask "Which of these did you mean? Reply with the number, or 'none' to
  abort." Do not auto-select a candidate. Only proceed to step 6 after the user names one.

**Step 6 — Preview-and-confirm gate (mandatory).**
Present the full preview of the pending change (the add table from step 4, or the resolved
removal text from step 5). Use AskUserQuestion to ask:

  "Apply this change? (yes / no / edit)"

- "yes" — proceed to step 7.
- "no" or any other response — abort. State "Aborted. No changes were written." Do not proceed.
- "edit" — ask what to change, apply the edit to the pending set (e.g. reword a question, swap a
  domain, change est_minutes), then repeat step 6 with the revised preview.

**Step 7 — Write questions.md first.**
Only proceed here after explicit "yes" from step 6.

For add: use Edit or Write to append each approved row at the end of questions.md in
pipe-delimited table format:

  `| <question text> | <domain> | <est_minutes> |`

For remove: use Edit to delete the exact line matching the resolved question text. Do not leave
blank lines or disturb any other row.

After writing, validate that the file remains a well-formed markdown table: read the file back,
count the pipe characters on each data row, confirm they match the header row (3 columns = 4
pipes per row). If any row has the wrong pipe count, fix it before continuing.

**Step 8 — Sync the Google Sheet.**
After questions.md has been written and validated, sync the change to the Bank tab.

For add, for each approved row in order:
  `python scripts/sheets_helper.py append --question "<question text>" --domain "<domain>" --est-minutes <n>`

Parse the JSON output from stdout. On exit 0, record `appended_row` from the response.

For remove:
  `python scripts/sheets_helper.py delete --question "<exact resolved question text>"`

Parse the JSON output from stdout. On exit 0, record `deleted_row` from the response.

Error handling:
- Exit 1 (auth/API error): surface the full stderr JSON to the user and stop. Do not retry.
- Exit 2 (delete — no match): surface the error. The row was already removed from questions.md
  in step 7. Tell the user the sheet was not updated and ask them to inspect manually.
- Exit 3 (delete — multiple matches): surface the stderr JSON listing the matching rows. Tell the
  user the sheet was not updated. Ask them to resolve the ambiguity in the sheet directly before
  retrying.

**Step 9 — Report.**
List every row written or deleted, with the sheet row index returned by the helper:

  - Added row at sheet row `<appended_row>`: `<question text>`
  - Deleted sheet row `<deleted_row>`: `<question text>`

State that questions.md and the Bank tab are now in sync.
</process>

## Output format

Preview every change as a `| question | domain | est_minutes |` table before writing. Confirm
removals by showing the exact resolved question text and the planned change.

Never reveal or hint at the answer to any question — not in previews, not in removal rationale,
not in error messages. If explaining why a question is borderline, describe the structural
problem (too broad, answer in the question, etc.) without giving the answer itself.

## Trigger forms

Inline — provide the direction and description together:

  `/curate-bank add 5 questions about why everyday materials behave unexpectedly`
  `/curate-bank remove the one about why ice cubes get cloudy in the center`
  `/curate-bank add 1 question about ice cube cloudiness`

Interactive — invoke with no arguments, then describe what you want once the skill prompts:

  `/curate-bank`
  → Skill asks: "Do you want to add or remove questions?"
  → You: "Add some questions about geology"
  → Skill asks: "How many, and any specific angle?"
  → Proceed from there.

## Source of truth

questions.md is the source of truth. The Google Sheet is a derived delivery surface. The skill
always writes questions.md first, then syncs the sheet — never the reverse.

## Failure modes

- **Helper script not found or Python deps missing:** `python scripts/sheets_helper.py` exits
  with a Python import error or file-not-found. Report the missing requirement (run
  `pip install -r scripts/requirements.txt` from the repo root) and stop. Do not attempt the
  sheet sync without the helper.

- **`.secrets/service-account.json` missing:** The helper will fail on its first API call with
  an auth error (exit 1, JSON on stderr). Surface the error message and instruct the user to
  complete Phase 3 Plan 02 (place the service account JSON at `.secrets/service-account.json`).
  The path is the only thing surfaced — never print or log the file contents.

- **Sheet API auth error (403 / 404):** Indicates the service account email is no longer an
  editor on the Bank sheet, or the sheet ID has changed. Surface the error from the helper's
  stderr JSON and instruct the user to re-share the sheet with
  `daily-learning-curator@daily-learning-499314.iam.gserviceaccount.com`.

- **Divergence detected mid-operation (step 3 fires after a partial write):** Abort immediately,
  surface the discrepancy, and ask the user to resolve the state manually before retrying. Do
  not attempt a partial sync.

- **questions.md pipe-count mismatch after write (step 7 validation):** Fix the malformed row
  before proceeding to step 8. If the fix is ambiguous, surface the problem row, abort, and
  restore the file to its pre-write state using the in-memory snapshot from step 2.
