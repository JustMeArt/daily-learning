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

One n8n workflow runs on a schedule:

**Daily Learning — Morning Questions** (runs at 06:30)
- Reads all `queued` questions from the Bank tab in Google Sheets
- Picks 3 at random
- Sends them via SendGrid
- Marks them as `sent` in the sheet

The `questions.md` file in this repo is the master question bank. New questions are imported from it into the Google Sheet using `scripts/sheets_helper.py`.

The workflow runs on a self-hosted n8n instance inside a Docker container on a DigitalOcean VPS — so the 06:30 email arrives whether or not your local machine is on.

---

## Hosting

The workflow runs on a DigitalOcean VPS (Ubuntu 24.04, $6/month) with n8n in Docker. Everything needed to reproduce the setup from scratch is in `deploy/`:

```
deploy/
  docker-compose.yml   — n8n container config (volume, restart policy, timezone)
  setup.md             — full step-by-step runbook: Droplet → SSH → firewall → Docker → n8n → credentials
```

Key decisions:
- **n8n in Docker** with `restart: always` — survives VPS reboots automatically
- **ufw firewall** — only ports 22 (SSH) and 5678 (n8n) open
- **Google Sheets** via service account (no OAuth redirect URI needed)
- **Email** via SendGrid API (DigitalOcean blocks outbound SMTP on new Droplets)
- No domain or SSL for now — n8n is accessible at `http://VPS-IP:5678`

---

## Setup

### 1. Google Sheet

Create a Google Sheet with one tab named **Bank** — columns: `question`, `domain`, `est_minutes`, `status`, `date_sent`.

Import questions from `questions.md` using the helper script (see below).

### 2. Google credentials

Create a service account in [Google Cloud Console](https://console.cloud.google.com), enable the Sheets API, download the JSON key and save it as `.secrets/service-account.json`. Share the sheet with the service account's email address (Editor access).

### 3. n8n workflow

Import `n8n-workflow.json` into your n8n instance. Set:
- Google Sheets credential → **Google Service Account API** (use the service-account.json from step 2)
- Send Email credential → **SendGrid** (requires a SendGrid account and verified sender)

For self-hosted n8n on a plain IP address (no domain): see `deploy/setup.md` for the full credential and hosting setup.

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
questions.md             — master question bank (375 questions, markdown table)
question-bank.md         — original 80 hand-written starter questions (8 domains)
question-bank-science.md — 50 science-domain starters (5 domains)
n8n-workflow.json        — importable n8n workflow (the live one)
sheet-setup.md           — Google Sheet structure reference
deploy/
  docker-compose.yml     — n8n container config for VPS hosting
  setup.md               — full VPS setup runbook
scripts/
  sheets_helper.py       — CLI tool: append/read/delete questions in the Sheet
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
