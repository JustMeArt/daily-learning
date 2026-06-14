---
name: curate-bank
description: Add or remove questions in the daily-learning bank using natural language. Applies the quality bar, writes to questions.md, and syncs the change to the Google Sheet Bank tab via scripts/sheets_helper.py. Use when the user wants to add new questions, remove existing ones, or refine the bank.
argument-hint: "[add <description>] [remove <description>]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

# Curate the daily-learning question bank

<objective>
Accept a loose natural-language intent (add questions about a topic, remove a question that isn't
working), apply the quality bar below, write the change to `questions.md` as the source of truth,
then sync to the Google Sheet Bank tab via `scripts/sheets_helper.py`. Every write is gated by a
preview-and-confirm step — nothing is written until the user explicitly approves.

**Flow:** Parse intent → Generate or identify questions → Preview → User approves → Write questions.md → Sync Google Sheet
</objective>

## Quality bar

Every question must pass all of these:

- **Ordinary** — about something the person meets in normal life, or a foundational fact worth refreshing.
- **Non-obvious** — hides a "huh, I never thought about that" answer. Most adults shouldn't already know it.
- **Specific** — one concrete thing, not a broad topic. "Why do recipes say to preheat?" not "How do ovens work?"
- **Findable** — answerable in one sitting from a single decent web page.
- **Spoiler-free** — the question must never reveal or hint at its own answer. This rule is absolute.

"Why is the sky blue?" is the low-water mark, not the target.

## Domains

`Kitchen & food` · `The body` · `Household objects & built environment` · `Social customs & language` · `Money & everyday systems` · `Nature, weather & everyday science` · `Everyday tech` · `Games & puzzles` · `Medicine & health` · `Biology & the living world` · `Earth & geology` · `Math & numbers` · `Space & sky`

New domains can be added. When adding a brand-new domain, generate 8–10 starters so it has range from day one.

Use the exact title-casing shown above when writing to `questions.md`.

`est_minutes` must be one of: `15`, `30`, `60`.

<context>
Arguments: $ARGUMENTS

- First token is `add` → route to Add flow
- First token is `remove` → route to Remove flow
- No arguments → use AskUserQuestion to ask "Do you want to add or remove questions?" then "Describe what you want to add or remove."
</context>

<process>

**Step 1 — Parse intent.**
Extract the leading flag (`add` or `remove`) from $ARGUMENTS. If absent, collect interactively. Record the direction and the description.

**Step 2 — Load questions.md.**
Read `questions.md` from the repo root. Parse every data row into `{ question, domain, est_minutes }` records. Used for duplicate detection (Add) and fuzzy matching (Remove).

**Step 3 — Divergence check (gate).**
Run `python scripts/sheets_helper.py read` from the repo root. Compare the question texts in its JSON output against `questions.md`.

If they differ, show what's out of sync and ask:
> "questions.md and the Bank tab are out of sync. How do you want to proceed?
> (a) continue anyway, (b) abort, (c) treat questions.md as truth and re-sync first."

- **(b)** → abort. State "Aborted. No changes were written."
- **(c)** → re-sync: append missing rows, delete extra rows, then continue.
- **(a)** → note the divergence (surfaced again in Step 9) and continue.

If in sync, continue directly.

**Step 4 — Add flow: generate candidates.**
Generate N questions matching the user's description. For each:
- Check for duplicates or near-duplicates against `questions.md` and drop any that are too similar.
- Assign the correct domain (exact title-casing from the list above).
- Assign `est_minutes` (15, 30, or 60).
- Emit a preview table:

  | question | domain | est_minutes |
  |---|---|---|
  | ... | ... | 15 |

Proceed to Step 6.

**Step 5 — Remove flow: resolve the target.**
Fuzzy-match the user's description against every question in `questions.md`.

- Zero matches → "No matching question found." Abort.
- One match → show the full question text. "Will delete this row from questions.md and the Bank tab." Proceed to Step 6.
- Multiple matches → list all candidates. Use AskUserQuestion: "Which did you mean? Reply with the number, or 'none' to abort." Do not auto-select.

**Step 6 — Preview-and-confirm gate (mandatory).**
Show the full pending change. Ask:

> "Apply this change? (yes / no / edit)"

- **yes** → proceed to Step 7.
- **no** → abort. "Aborted. No changes were written."
- **edit** → ask what to change, apply it, repeat Step 6 with the revised preview.

**Step 7 — Write questions.md.**
Only after explicit "yes" from Step 6.

- Add: append each row at the end in pipe-delimited format: `| <question> | <domain> | <est_minutes> |`
- Remove: delete the exact matching line. Leave no blank lines.

Validate the file is still a well-formed markdown table (4 pipes per data row). Fix any malformed row before continuing.

**Step 8 — Sync the Google Sheet.**

Add: for each row in order:
```
python scripts/sheets_helper.py append --question "<text>" --domain "<domain>" --est-minutes <n>
```

Remove:
```
python scripts/sheets_helper.py delete --question "<exact text>"
```

Error handling:
- Exit 1 (auth/API error) → surface stderr to user, stop.
- Exit 2 (delete — no match) → surface error. Tell user the sheet was not updated and to inspect manually.
- Exit 3 (delete — multiple matches) → surface stderr. Ask user to resolve in the sheet directly.

If `scripts/sheets_helper.py` can't be found or fails to import, prompt the user to run `pip install -r scripts/requirements.txt` from the repo root.

**Step 9 — Report.**
List every row written or deleted with the sheet row index returned by the helper.

If a pre-existing divergence was acknowledged at Step 3, note: "Change applied. The pre-existing divergence from Step 3 is still unresolved — reconcile the Bank tab manually."

Otherwise: "questions.md and the Bank tab are now in sync."

</process>

## Output format

Always preview changes as a `| question | domain | est_minutes |` table before writing. Confirm removals by showing the exact resolved question text.

Never reveal or hint at the answer to any question — not in previews, not in error messages.

## Usage examples

```
/curate-bank add 5 questions about why everyday materials behave unexpectedly
/curate-bank remove the one about why ice cubes get cloudy
/curate-bank add questions about geology
/curate-bank
```

## Setup required

The Google Sheet sync needs credentials in `.secrets/`:
- `service-account.json` — a Google service account with editor access to your Bank sheet
- Run `scripts/verify_sheet_access.sh` to confirm auth is working

Without `.secrets/`, `questions.md` writes still work — only the Sheet sync fails.
