#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! test -f .secrets/service-account.json; then
    echo "Missing .secrets/service-account.json — run Plan 02 Task 1 first" >&2
    exit 1
fi

OUTPUT=$(python scripts/sheets_helper.py read)

COUNT=$(echo "$OUTPUT" | python -c "import json,sys; data=json.load(sys.stdin); print(len(data))")

if [ "$COUNT" -lt 130 ]; then
    echo "verify_sheet_access: FAIL — only $COUNT rows returned from Bank tab (expected >= 130). Check sheet seed data and service account access." >&2
    exit 2
fi

echo "verify_sheet_access: OK — read $COUNT rows from Bank tab"
