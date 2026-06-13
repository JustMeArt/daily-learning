---
phase: 03-curator-agent
plan: 01
subsystem: infra
tags: [google-sheets-api, service-account, python, google-auth, google-api-python-client]

# Dependency graph
requires:
  - phase: 03-context
    provides: sheet ID, credential placement convention (D-01 through D-03)
provides:
  - .gitignore excluding .secrets/ directory (blocks credential commits)
  - .secrets/ directory placeholder for service-account.json
  - scripts/requirements.txt pinning google-auth + google-api-python-client
  - scripts/sheets_helper.py CLI with read/append/delete subcommands + test suite
affects: [03-02, 03-03]

# Tech tracking
tech-stack:
  added:
    - google-auth==2.35.0
    - google-auth-httplib2==0.2.0
    - google-api-python-client==2.149.0
    - pytest (dev)
  patterns:
    - Service account auth via from_service_account_file + googleapiclient.discovery.build
    - argparse subparsers for multi-subcommand CLI
    - JSON to stdout on success, JSON to stderr on error (all subcommands)
    - Exit codes: 0=success, 1=auth/API error, 2=no match, 3=multiple matches

key-files:
  created:
    - .gitignore
    - .secrets/.gitkeep (local only, gitignored)
    - scripts/requirements.txt
    - scripts/__init__.py
    - scripts/sheets_helper.py
    - scripts/test_sheets_helper.py
  modified: []

key-decisions:
  - "scripts/__init__.py added so tests can import scripts.sheets_helper as a package from repo root"
  - ".secrets/.gitkeep is created on disk but cannot be committed — directory is gitignored as intended (T-03-01 mitigation verified via git check-ignore)"
  - "batchUpdate deleteDimension uses 0-based startIndex/endIndex derived from 1-based row number"

patterns-established:
  - "Sheets helper CLI contract: read → JSON array, append → {appended_row, question}, delete → {deleted_row, question} or exit 2/3"
  - "All API errors surfaced as JSON on stderr with non-zero exit; callers should check exit code before parsing stdout"

requirements-completed:
  - FUTURE-01

# Metrics
duration: 4min
completed: 2026-06-13
---

# Phase 3 Plan 01: Curator Agent — Repo Foundations and Sheets Helper Summary

**Python CLI helper (scripts/sheets_helper.py) with read/append/delete subcommands against the Bank tab via service account auth, with git-ignored .secrets/ and pinned dependencies**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-06-13T17:54:02Z
- **Completed:** 2026-06-13T17:57:43Z
- **Tasks:** 2 (Task 1: foundations, Task 2: TDD implementation)
- **Files modified:** 6 created

## Accomplishments
- .gitignore blocks accidental commit of .secrets/service-account.json (verified via git check-ignore)
- scripts/requirements.txt pins exact versions of all Google API client libraries
- scripts/sheets_helper.py delivers complete CLI contract: read, append, delete with specified exit codes
- Test suite (6 tests) covers all subcommands using mocked Sheets API — runs offline, all pass

## Helper CLI Contract (verbatim — for Plan 03 reference)

```
python scripts/sheets_helper.py read
  → stdout: JSON array of row objects
  [{"row": 2, "question": "...", "domain": "...", "est_minutes": "15", "status": "queued", "date_sent": ""}, ...]
  → exit 0 on success, exit 1 on auth/API error (JSON on stderr)

python scripts/sheets_helper.py append --question "..." --domain "..." --est-minutes 15
  → appends one row: status=queued, date_sent=""
  → stdout: {"appended_row": <row_index>, "question": "..."}
  → exit 0 on success

python scripts/sheets_helper.py delete --question "<exact question text>"
  → finds row matching question column exactly, deletes it
  → stdout: {"deleted_row": <row_index>, "question": "..."}
  → exit 2 if no match (JSON error on stderr)
  → exit 3 if multiple matches (JSON with row indices on stderr)
  → exit 0 on single successful match + delete
```

Constants embedded in script:
```python
SPREADSHEET_ID = "16zTv6lo9SXhZdcorvfhieB46wzbVDwNTDZCpriJdNlE"
SHEET_NAME = "Bank"
CREDENTIALS_PATH = ".secrets/service-account.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
```

## Task Commits

Each task was committed atomically:

1. **Task 1: Repo foundations** - `a7d55e4` (chore)
2. **Task 2 RED: Failing tests** - `32893d8` (test)
3. **Task 2 GREEN: Implementation** - `b5bf393` (feat)

**Plan metadata:** (docs commit — recorded below)

_Note: Task 2 is TDD — test commit precedes feat commit._

## Files Created/Modified
- `.gitignore` — excludes .secrets/, __pycache__/, .venv/ and standard Python noise
- `.secrets/.gitkeep` — local placeholder only; not committed (gitignored per T-03-01)
- `scripts/requirements.txt` — pinned: google-auth==2.35.0, google-auth-httplib2==0.2.0, google-api-python-client==2.149.0
- `scripts/__init__.py` — empty init to enable `import scripts.sheets_helper` from repo root
- `scripts/sheets_helper.py` — full CLI implementation (argparse subparsers, service account auth, read/append/delete)
- `scripts/test_sheets_helper.py` — 6 pytest tests covering all behaviors, mocked API, runs offline

## Decisions Made
- Added `scripts/__init__.py` so test file can import the helper as `scripts.sheets_helper` from the repo root (required by pytest discovery pattern). Not in the original plan but needed for the test structure specified in the plan.
- `.secrets/.gitkeep` is not committable (the directory is gitignored), so only the other two Task 1 files are tracked in git. The directory exists on disk for the credential drop-in in Plan 02.
- T-03-01 mitigation verified: `git check-ignore .secrets/service-account.json` exits 0.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added scripts/__init__.py for package import**
- **Found during:** Task 2 RED phase
- **Issue:** Test file uses `import scripts.sheets_helper as helper` which requires scripts/ to be a Python package. Without __init__.py, the import fails with ModuleNotFoundError.
- **Fix:** Created empty `scripts/__init__.py` alongside the test file.
- **Files modified:** scripts/__init__.py
- **Verification:** pytest immediately began importing the module (failing on missing file, as expected in RED)
- **Committed in:** 32893d8 (RED phase commit, alongside test file)

---

**Total deviations:** 1 auto-fixed (Rule 2 — missing critical file for correct operation)
**Impact on plan:** Necessary for the test infrastructure the plan itself specified. No scope creep.

## Issues Encountered
- System Python on Arch Linux has PEP 668 restrictions (externally managed). Used `--break-system-packages` flag to install pytest and Google API libraries for the test run.

## User Setup Required
Plan 02 handles the actual service account credential setup. For now:
- `.secrets/` directory exists locally (gitignored)
- Drop `service-account.json` from Google Cloud Console into `.secrets/` when ready
- Run `pip install -r scripts/requirements.txt` before invoking the helper

## Known Stubs
None — the helper is complete and functional. The only "missing piece" is the real credential file, which is intentionally deferred to Plan 02.

## Threat Flags
None — no new network endpoints, auth paths, or schema changes beyond what the plan's threat model already covers (T-03-01 through T-03-05, T-03-SC all addressed in implementation).

## Next Phase Readiness
- Plan 02 can drop `service-account.json` into `.secrets/` and run `python scripts/sheets_helper.py read` against the live sheet immediately
- Plan 03 (`curate-bank` SKILL.md) can reference the CLI contract above verbatim — the interface is stable
- No blockers

---
*Phase: 03-curator-agent*
*Completed: 2026-06-13*
