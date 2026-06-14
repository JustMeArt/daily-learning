# Google Sheet setup — daily-learning

## 1. Create the sheet

Go to **https://sheets.new** — this opens a blank Google Sheet immediately.
Rename it **daily-learning** (click "Untitled spreadsheet" at the top left).

## 2. Rename the default tab

Double-click the **Sheet1** tab at the bottom → rename it **Bank**.

## 3. Bank tab — headers (row 1)

In row 1, enter these values one per column (A through E):

| A | B | C | D | E |
|---|---|---|---|---|
| question | domain | est_minutes | status | date_sent |

## 4. Import questions

Use `scripts/sheets_helper.py` to populate the sheet from `questions.md`:

```bash
cd scripts
pip install -r requirements.txt
python sheets_helper.py append --question "..." --domain "..." --est-minutes 15
```

Or use the `/curate-bank` Claude Code skill to add questions in plain English.

New rows are added with `status = queued` and `date_sent` blank. The n8n workflow reads all `queued` rows, picks 3 at random each morning, sends them, then marks them `sent`.

## 5. Share with n8n

The workflow authenticates via a Google service account. Save the service account JSON key to `.secrets/service-account.json` and share the sheet with the service account email (Editor access).

Copy the sheet ID from the URL:

```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
```

The sheet ID is already hardcoded in `scripts/sheets_helper.py`. If you create a fresh sheet, update `SPREADSHEET_ID` in that file and in the Google Sheets nodes inside `n8n-workflow.json`.
