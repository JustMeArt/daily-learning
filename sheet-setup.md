# Google Sheet setup — daily-learning

## 1. Create the sheet

Go to **https://sheets.new** — this opens a blank Google Sheet immediately.
Rename it **daily-learning** (click "Untitled spreadsheet" at the top left).

## 2. Create two tabs

At the bottom of the sheet you'll see a tab called "Sheet1".

1. Double-click **Sheet1** → rename it **Queue**.
2. Click the **+** button to add a second tab → rename it **Domains**.

## 3. Queue tab — headers (row 1)

Click the **Queue** tab. In row 1, enter these values one per column (A through F):

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| date_added | question | domain | est_minutes | status | date_sent |

## 4. Domains tab — headers and data

Click the **Domains** tab.

**Row 1 headers** (columns A and B):

| A | B |
|---|---|
| domain | last_used |

**Rows 2–14 — paste these 13 values into column A:**

```
kitchen & food
the body
household objects & built environment
social customs & language
money & everyday systems
nature, weather & everyday science
everyday tech
games & puzzles
medicine & health
biology & the living world
earth & geology
math & numbers
space & sky
```

Leave column B (last_used) blank for now — Workflow A will fill it in.

## 5. Share with n8n

In n8n, the Google Sheets node authenticates via OAuth2 or a Service Account.
Whichever you use, make sure the Google account (or service account email) has
**Editor** access to this sheet. Copy the sheet ID from the URL:

```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
```

You'll paste that ID into every Google Sheets node in both workflows.
