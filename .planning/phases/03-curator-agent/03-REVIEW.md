---
phase: 03-curator-agent
reviewed: 2026-06-13T20:30:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - scripts/requirements.txt
  - scripts/__init__.py
  - scripts/sheets_helper.py
  - scripts/test_sheets_helper.py
  - scripts/verify_sheet_access.sh
  - .claude/skills/curate-bank/SKILL.md
findings:
  critical: 1
  warning: 5
  info: 3
  total: 9
  fixed: 6
  skipped: 0
status: fixed
---

# Phase 03: Code Review Report

**Reviewed:** 2026-06-13T20:30:00Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Reviewed the curator agent implementation: a Google Sheets helper CLI (`sheets_helper.py`), its test suite, a shell verification script, and the `curate-bank` skill definition. The core delete/append logic is structurally sound and the row index math is correct. The most serious finding is a credential path resolved relative to the process working directory, which silently silences authentication with no useful error when the script is invoked from outside the repo root. Additional warnings cover: no validation of `est_minutes` against the allowed set (15/30/60), a silent `-1` appended_row on API response truncation, a misleading "now in sync" claim in the skill after a divergence-acknowledged continue, an under-specified re-sync option in the divergence gate, and the test suite not asserting the `sheetId` in the `deleteDimension` body.

---

## Critical Issues

### CR-01: CREDENTIALS_PATH is CWD-relative — silently fails when invoked from any directory other than repo root

**File:** `scripts/sheets_helper.py:19`

**Issue:** `CREDENTIALS_PATH = ".secrets/service-account.json"` is a relative path that is resolved against whatever the process working directory is at runtime. If `sheets_helper.py` is called directly from any directory other than the repo root (e.g., `python daily-learning/scripts/sheets_helper.py read`), `os.path.exists(CREDENTIALS_PATH)` returns `False` and the script exits with `"credentials not found"` even though the file exists. The error message tells the user to place the file at `.secrets/service-account.json`, which misleads them into thinking the credential is missing rather than that the CWD is wrong.

`verify_sheet_access.sh` works around this by `cd`-ing to the repo root first, but any caller that does not follow the same convention will see cryptic auth failures.

**Fix:** Resolve the path relative to the script file, not the CWD:
```python
import pathlib
_SCRIPT_DIR = pathlib.Path(__file__).parent.parent  # repo root
CREDENTIALS_PATH = str(_SCRIPT_DIR / ".secrets" / "service-account.json")
```

---

## Warnings

### WR-01: `est_minutes` is not validated against the allowed set {15, 30, 60}

**File:** `scripts/sheets_helper.py:237`

**Issue:** The help text says "Estimated minutes (15, 30, or 60)" but `argparse` accepts any integer. Passing `--est-minutes 99` writes `"99"` to the sheet silently. The n8n workflow and the SKILL.md both depend on est_minutes carrying a meaning; invalid values corrupt the bank without any error.

**Fix:** Add a `choices` constraint or a manual validation after `parse_args()`:
```python
append_parser.add_argument(
    "--est-minutes",
    type=int,
    choices=[15, 30, 60],
    required=True,
    help="Estimated minutes (15, 30, or 60)",
)
```

### WR-02: `cmd_append` emits exit 0 with `appended_row: -1` when the API returns no `updatedRange`

**File:** `scripts/sheets_helper.py:139-145`

**Issue:** When the Sheets API omits the `updates.updatedRange` key (which can happen on quota errors or when the append is a no-op), `_parse_row_index_from_range("")` returns `-1`. The script prints `{"appended_row": -1, "question": ...}` and exits 0, making the caller believe the append succeeded. The SKILL.md step 8 says "On exit 0, record `appended_row` from the response" — so `-1` propagates into the step 9 report as a valid row number.

**Fix:** Treat `appended_row == -1` as an error:
```python
appended_row = _parse_row_index_from_range(updated_range)
if appended_row == -1:
    print(
        json.dumps({"error": "append_failed", "detail": "API returned no updatedRange", "question": args.question}),
        file=sys.stderr,
    )
    sys.exit(1)
```

### WR-03: Step 9 unconditionally claims sync when the user chose "continue anyway" at the divergence gate

**File:** `.claude/skills/curate-bank/SKILL.md:161`

**Issue:** Step 3 offers three divergence responses: (a) continue anyway, (b) abort, (c) re-sync. If the user picks (a), the state before the operation was divergent; the new operation adds or removes exactly one item. Step 9 then instructs: "State that questions.md and the Bank tab are now in sync." This is a false statement whenever option (a) was taken, because the pre-existing divergence is still present after the new operation. An agent following these instructions literally will produce a misleading confirmation.

**Fix:** Add a conditional to step 9:
```
If the user selected option (a) at the divergence gate in step 3, do NOT state that the
files are in sync. Instead state: "Change applied. Note: the pre-existing divergence from
step 3 is still unresolved — you may want to reconcile the Bank tab manually."
```

### WR-04: Option (c) "treat questions.md as truth and re-sync" at the divergence gate is undefined

**File:** `.claude/skills/curate-bank/SKILL.md:69-74`

**Issue:** The divergence gate (step 3) offers option (c): "treat questions.md as truth and re-sync after the change." No step in the process defines what re-syncing entails — there is no step 3c, no mention of which rows to append/delete in the sheet, and no loop. An LLM following this skill will improvise the re-sync behavior, likely producing an incorrect or incomplete result.

**Fix:** Define the re-sync procedure explicitly. At minimum:
```
If user picks (c):
  - For each question in questions.md but not in the sheet: run the append subcommand.
  - For each question in the sheet but not in questions.md: run the delete subcommand.
  - After re-sync, continue with the user's original intent (step 4 or 5).
```

### WR-05: Test for `delete` does not assert the correct `sheetId` is passed in `deleteDimension`

**File:** `scripts/test_sheets_helper.py:160-169`

**Issue:** `test_delete_single_match_calls_batch_update` asserts `dimension`, `startIndex`, and `endIndex` in the `deleteDimension` request body, but does not assert `del_req["sheetId"]`. The mock returns `sheetId: 0` and the production code passes `bank_sheet_id` into the request. If a future refactor accidentally passed the wrong sheet ID (e.g., `0` hardcoded instead of the looked-up value), this test would not catch it. The test also does not assert that `_get_bank_sheet_id` was actually called.

**Fix:**
```python
assert del_req["sheetId"] == 0  # matches fake spreadsheet_meta in _make_fake_service
```

---

## Info

### IN-01: No test coverage for `cmd_read` with an empty sheet (zero rows returned)

**File:** `scripts/test_sheets_helper.py`

**Issue:** `cmd_read` has an early-exit path (`if not rows: print(json.dumps([])); sys.exit(0)`) that is never exercised by the test suite. The current tests all supply a header + data rows.

**Fix:** Add a test that supplies `get_response={"values": []}` (or `get_response={}`) and asserts that the output is `[]` with exit code 0.

### IN-02: `verify_sheet_access.sh` produces a Python traceback on malformed/empty `sheets_helper.py` output

**File:** `scripts/verify_sheet_access.sh:13`

**Issue:** The inline `python -c "import json,sys; data=json.load(sys.stdin); print(len(data))"` will raise `json.JSONDecodeError` and print a Python traceback to stderr if `OUTPUT` is empty or not valid JSON. While `set -euo pipefail` causes the script to exit non-zero (correct), the error message is unhelpful. This can occur if `sheets_helper.py` exits 0 but writes nothing to stdout (which would be a bug in the helper, but defensive handling here is cheap).

**Fix:** Wrap the parse in a try/except or pipe through `python3`:
```bash
COUNT=$(echo "$OUTPUT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(len(data))
except Exception as e:
    print(f'verify_sheet_access: FAIL — could not parse sheets_helper output: {e}', file=sys.stderr)
    sys.exit(1)
")
```

### IN-03: `test_missing_credentials_exits_nonzero` assertion passes for the wrong reason

**File:** `scripts/test_sheets_helper.py:253`

**Issue:** The test patches `CREDENTIALS_PATH` to a tmp path, then asserts:
```python
assert ".secrets/service-account.json" in captured.err or str(tmp_path / "no-such-file.json") in captured.err
```
The assertion passes because the error message has a hardcoded string `"save it as .secrets/service-account.json"`, not because the patched path appears in the error. The test would still pass even if the `{CREDENTIALS_PATH}` interpolation in the error message were broken. The test provides weaker coverage than it appears to.

**Fix:** Assert only the patched path (the concrete thing being tested), not the hardcoded fallback:
```python
assert str(tmp_path / "no-such-file.json") in captured.err
```

---

_Reviewed: 2026-06-13T20:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
