"""
Google Sheets helper for the Bank tab — CLI interface for the curate-bank skill.

Subcommands:
  python scripts/sheets_helper.py read
  python scripts/sheets_helper.py append --question "..." --domain "..." --est-minutes 15
  python scripts/sheets_helper.py delete --question "..."

Authentication: requires .secrets/service-account.json (Google service account key).
"""

import argparse
import json
import sys
import os
import pathlib

_SCRIPT_DIR = pathlib.Path(__file__).parent.parent  # repo root
SPREADSHEET_ID = "16zTv6lo9SXhZdcorvfhieB46wzbVDwNTDZCpriJdNlE"
SHEET_NAME = "Bank"
CREDENTIALS_PATH = str(_SCRIPT_DIR / ".secrets" / "service-account.json")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _build_service():
    """Load service account credentials and return a Sheets API service client."""
    if not os.path.exists(CREDENTIALS_PATH):
        print(
            json.dumps(
                {
                    "error": "credentials not found",
                    "path": CREDENTIALS_PATH,
                    "message": (
                        f"Service account key not found at {CREDENTIALS_PATH}. "
                        "Download the JSON key from Google Cloud Console and save it as "
                        ".secrets/service-account.json"
                    ),
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _get_all_rows(service):
    """Return all rows from the Bank tab (including header).  Each row is a list of strings."""
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A:E")
        .execute()
    )
    return result.get("values", [])


def _get_bank_sheet_id(service):
    """Return the numeric sheetId for the Bank tab."""
    meta = (
        service.spreadsheets()
        .get(spreadsheetId=SPREADSHEET_ID, fields="sheets(properties(sheetId,title))")
        .execute()
    )
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("title") == SHEET_NAME:
            return props["sheetId"]
    raise RuntimeError(f"Sheet named '{SHEET_NAME}' not found in spreadsheet.")


def _parse_row_index_from_range(updated_range: str) -> int:
    """Parse the 1-based row number from a range string like 'Bank!A3:E3'."""
    # updated_range format: "SheetName!ARow:ERow"
    try:
        # take the part after '!'
        cell_range = updated_range.split("!")[1]
        # take the start cell e.g. 'A3'
        start_cell = cell_range.split(":")[0]
        # strip column letter(s)
        row_str = "".join(c for c in start_cell if c.isdigit())
        return int(row_str)
    except (IndexError, ValueError):
        return -1


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_read(args, service):
    rows = _get_all_rows(service)
    if not rows:
        print(json.dumps([]))
        sys.exit(0)

    # Skip header row (index 0); data rows start at index 1 → row 2 (1-based with header)
    header = rows[0]
    data_rows = rows[1:]

    output = []
    for i, row in enumerate(data_rows):
        # Pad row to 5 columns in case trailing empty cells are omitted
        padded = row + [""] * (5 - len(row))
        output.append(
            {
                "row": i + 2,  # header is row 1; first data row is row 2
                "question": padded[0],
                "domain": padded[1],
                "est_minutes": padded[2],
                "status": padded[3],
                "date_sent": padded[4],
            }
        )

    print(json.dumps(output))
    sys.exit(0)


def cmd_append(args, service):
    values = [[args.question, args.domain, str(args.est_minutes), "queued", ""]]
    response = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body={"values": values},
        )
        .execute()
    )

    updated_range = (
        response.get("updates", {}).get("updatedRange", "")
    )
    appended_row = _parse_row_index_from_range(updated_range)

    if appended_row == -1:
        print(
            json.dumps({
                "error": "append_failed",
                "detail": "API returned no updatedRange",
                "question": args.question,
            }),
            file=sys.stderr,
        )
        sys.exit(1)

    print(json.dumps({"appended_row": appended_row, "question": args.question}))
    sys.exit(0)


def cmd_delete(args, service):
    rows = _get_all_rows(service)
    if not rows:
        print(
            json.dumps({"error": "no match", "question": args.question}),
            file=sys.stderr,
        )
        sys.exit(2)

    # Skip header (row index 0 in list → row 1 in sheet)
    data_rows = rows[1:]
    matches = []
    for i, row in enumerate(data_rows):
        question_text = row[0] if row else ""
        if question_text == args.question:
            sheet_row = i + 2  # 1-based, header is row 1
            matches.append(sheet_row)

    if len(matches) == 0:
        print(
            json.dumps({"error": "no match", "question": args.question}),
            file=sys.stderr,
        )
        sys.exit(2)

    if len(matches) > 1:
        print(
            json.dumps(
                {
                    "error": "multiple matches",
                    "rows": matches,
                    "question": args.question,
                }
            ),
            file=sys.stderr,
        )
        sys.exit(3)

    # Exactly one match
    sheet_row = matches[0]
    bank_sheet_id = _get_bank_sheet_id(service)

    # Sheets API deleteDimension uses 0-based startIndex/endIndex
    start_index = sheet_row - 1
    end_index = sheet_row

    service.spreadsheets().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [
                {
                    "deleteDimension": {
                        "range": {
                            "sheetId": bank_sheet_id,
                            "dimension": "ROWS",
                            "startIndex": start_index,
                            "endIndex": end_index,
                        }
                    }
                }
            ]
        },
    ).execute()

    print(json.dumps({"deleted_row": sheet_row, "question": args.question}))
    sys.exit(0)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Google Sheets Bank tab helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # read
    subparsers.add_parser("read", help="Read all rows from the Bank tab as JSON")

    # append
    append_parser = subparsers.add_parser(
        "append", help="Append a new queued question to the Bank tab"
    )
    append_parser.add_argument("--question", required=True, help="Question text")
    append_parser.add_argument("--domain", required=True, help="Domain name")
    append_parser.add_argument(
        "--est-minutes",
        type=int,
        choices=[15, 30, 60],
        required=True,
        help="Estimated minutes (15, 30, or 60)",
    )

    # delete
    delete_parser = subparsers.add_parser(
        "delete", help="Delete a row matching the exact question text"
    )
    delete_parser.add_argument(
        "--question", required=True, help="Exact question text to find and delete"
    )

    args = parser.parse_args()

    try:
        service = _build_service()
    except SystemExit:
        raise
    except Exception as exc:
        print(
            json.dumps({"error": "auth_failed", "detail": str(exc)}),
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        if args.command == "read":
            cmd_read(args, service)
        elif args.command == "append":
            cmd_append(args, service)
        elif args.command == "delete":
            cmd_delete(args, service)
    except SystemExit:
        raise
    except Exception as exc:
        print(
            json.dumps({"error": "api_error", "detail": str(exc)}),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
