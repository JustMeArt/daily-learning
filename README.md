# Daily Learning

A daily curiosity question bank paired with an n8n email workflow. Every morning at 06:30, three questions land in your inbox — each one hiding a non-obvious answer about something ordinary.

375 questions across 13 domains, seeded by hand and extended via the [instagram-scraper](https://github.com/JustMeArt/instagram-scraper) pipeline.

---

## What it looks like

```
Your 3 questions for today:

1. Why does bread go stale faster in the fridge than on the counter?
   Domain: Kitchen & food · ~15 min

2. Why do public restroom stall doors have a gap at the bottom?
   Domain: Household objects & built environment · ~15 min

3. Why is the angle of the North Star above the horizon the same as your latitude?
   Domain: Space & sky · ~15 min
```

No answers in the email. You look them up. That's the point.

---

## How it works

Two n8n workflows run on a schedule:

**Workflow A — queue filler** (runs at 05:00)
- Checks how many questions are queued in Google Sheets
- If fewer than 7: picks the least-recently-used domain, calls Claude API to generate a new question, adds it to the queue

**Workflow B — daily emailer** (runs at 06:30)
- Picks the 3 oldest queued questions
- Sends them via Gmail
- Marks them as sent in the sheet

The `questions.md` file in this repo is the master question bank. New questions are imported from it into the Google Sheet using `scripts/sheets_helper.py`.

---

## Setup

### 1. Google Sheet

Create a Google Sheet with two tabs:

**Bank tab** — columns: `question`, `domain`, `est_minutes`
Import questions from `questions.md` using the helper script (see below).

**Queue tab** — columns: `date_added`, `question`, `domain`, `est_minutes`, `status`, `date_sent`

**Domains tab** — columns: `domain`, `last_used`
List all 13 domain names, leave `last_used` blank initially.

### 2. Google credentials

Enable the Google Sheets API in [Google Cloud Console](https://console.cloud.google.com). Download `credentials.json` and place it in `.secrets/`. On first run of `sheets_helper.py`, you'll be prompted to authorise — a `token.json` will be saved to `.secrets/` for future runs.

### 3. n8n workflows

Copy the node-by-node specs from `n8n-workflow-a.md` and `n8n-workflow-b.md` into your n8n instance. Set:
- Google Sheets credential (OAuth)
- Gmail credential (OAuth)
- Anthropic API key (for Workflow A's HTTP Request node)

### 4. Import the question bank into Google Sheets

```bash
cd scripts
pip install -r requirements.txt
python sheets_helper.py append --question "..." --domain "..." --est-minutes 15
```

Or bulk-import using the [instagram-scraper](https://github.com/JustMeArt/instagram-scraper) pipeline, which writes directly to `questions.md` and syncs to the sheet automatically.

---

## Files

```
questions.md            — master question bank (375 questions, markdown table)
question-bank.md        — original 80 hand-written starter questions (8 domains)
question-bank-science.md — 50 science-domain starters (5 domains)
n8n-workflow-a.md       — queue filler workflow spec (node by node)
n8n-workflow-b.md       — daily emailer workflow spec (node by node)
sheet-setup.md          — Google Sheet structure reference
scripts/
  sheets_helper.py      — CLI tool: append/read/delete questions in the Sheet
  verify_sheet_access.sh — quick auth check
```

---

## Claude Code skill

If you use [Claude Code](https://claude.ai/code), a `/curate-bank` skill is included in this repo. It lets you add or remove questions from the bank using plain English — no manual file editing.

```
/curate-bank add 5 questions about why everyday materials behave unexpectedly
/curate-bank remove the one about why ice cubes get cloudy
/curate-bank
```

The skill applies the quality bar automatically, shows a preview table before writing anything, and syncs the change to your Google Sheet. It lives in `.github/skills/curate-bank/` and is picked up by Claude Code automatically when you open the project.

---

## The question bar

Every question must pass all four:

1. **Specific** — one concrete thing, not a broad topic
2. **Non-obvious** — most people don't already know the answer
3. **Findable** — answerable from one decent page
4. **Self-concealing** — reading the question doesn't reveal the answer

"Why is the sky blue?" is the low-water mark, not the target.

---

## Domains

Kitchen & food · The body · Household objects & built environment · Social customs & language · Money & everyday systems · Nature, weather & everyday science · Everyday tech · Games & puzzles · Medicine & health · Biology & the living world · Earth & geology · Math & numbers · Space & sky

---

## Adding more questions

**Manually** — add a row to `questions.md` and run `sheets_helper.py append`.

**From an Instagram creator** — use the [instagram-scraper](https://github.com/JustMeArt/instagram-scraper) pipeline. It downloads, transcribes, and extracts questions automatically, then writes approved ones directly to `questions.md` and syncs to the Sheet.
