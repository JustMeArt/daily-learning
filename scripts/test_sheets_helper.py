"""
Tests for scripts/sheets_helper.py

Uses unittest.mock to patch googleapiclient.discovery.build so tests run offline.
"""

import json
import sys
import types
from unittest.mock import MagicMock, patch, call
import pytest

# ---------------------------------------------------------------------------
# Helpers to run the CLI subcommands by calling main() after patching argv
# ---------------------------------------------------------------------------

def _make_fake_sheets_values(rows):
    """Return a fake API response dict for values().get().execute()"""
    return {"values": rows}


def _make_fake_service(get_response=None, append_response=None, batch_response=None, spreadsheet_meta=None):
    """Build a layered mock matching the googleapiclient.discovery service interface."""
    svc = MagicMock()

    # spreadsheets().values().get().execute()
    svc.spreadsheets.return_value.values.return_value.get.return_value.execute.return_value = (
        get_response or {"values": []}
    )

    # spreadsheets().values().append().execute()
    svc.spreadsheets.return_value.values.return_value.append.return_value.execute.return_value = (
        append_response or {}
    )

    # spreadsheets().batchUpdate().execute()
    svc.spreadsheets.return_value.batchUpdate.return_value.execute.return_value = (
        batch_response or {}
    )

    # spreadsheets().get().execute() — for sheet-id lookup
    svc.spreadsheets.return_value.get.return_value.execute.return_value = (
        spreadsheet_meta or {
            "sheets": [
                {"properties": {"sheetId": 0, "title": "Bank"}}
            ]
        }
    )

    return svc


# ---------------------------------------------------------------------------
# Test 1 — read subcommand returns JSON array of row objects
# ---------------------------------------------------------------------------

def test_read_returns_row_objects(monkeypatch, capsys):
    fake_data = {
        "values": [
            # header
            ["question", "domain", "est_minutes", "status", "date_sent"],
            # data rows
            ["Why is ice slippery?", "The body", "15", "queued", ""],
            ["Why does salt melt ice?", "Kitchen & food", "30", "sent", "2026-06-01"],
        ]
    }
    fake_svc = _make_fake_service(get_response=fake_data)

    import scripts.sheets_helper as helper
    monkeypatch.setattr(helper, "_build_service", lambda: fake_svc)

    monkeypatch.setattr(sys, "argv", ["sheets_helper.py", "read"])
    with pytest.raises(SystemExit) as exc:
        helper.main()
    assert exc.value.code == 0

    captured = capsys.readouterr()
    rows = json.loads(captured.out)
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert rows[0] == {
        "row": 2,
        "question": "Why is ice slippery?",
        "domain": "The body",
        "est_minutes": "15",
        "status": "queued",
        "date_sent": "",
    }
    assert rows[1]["row"] == 3
    assert rows[1]["question"] == "Why does salt melt ice?"


# ---------------------------------------------------------------------------
# Test 2 — append subcommand calls values().append with correct args
# ---------------------------------------------------------------------------

def test_append_calls_api_correctly(monkeypatch, capsys):
    append_resp = {
        "updates": {
            "updatedRange": "Bank!A3:E3",
            "updatedRows": 1,
        }
    }
    fake_svc = _make_fake_service(append_response=append_resp)

    import scripts.sheets_helper as helper
    monkeypatch.setattr(helper, "_build_service", lambda: fake_svc)
    monkeypatch.setattr(sys, "argv", [
        "sheets_helper.py", "append",
        "--question", "Why does X happen?",
        "--domain", "The body",
        "--est-minutes", "15",
    ])

    with pytest.raises(SystemExit) as exc:
        helper.main()
    assert exc.value.code == 0

    # Verify the append call was made
    append_call = fake_svc.spreadsheets.return_value.values.return_value.append
    append_call.assert_called_once()
    kwargs = append_call.call_args
    assert kwargs[1]["range"] == "Bank!A:E"
    assert kwargs[1]["body"]["values"] == [["Why does X happen?", "The body", "15", "queued", ""]]
    assert kwargs[1]["valueInputOption"] == "RAW"

    # Verify stdout
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["question"] == "Why does X happen?"
    assert "appended_row" in result


# ---------------------------------------------------------------------------
# Test 3 — delete subcommand finds row and calls batchUpdate
# ---------------------------------------------------------------------------

def test_delete_single_match_calls_batch_update(monkeypatch, capsys):
    fake_data = {
        "values": [
            ["question", "domain", "est_minutes", "status", "date_sent"],
            ["Why does X happen?", "The body", "15", "queued", ""],
            ["Why is grass green?", "Nature & weather", "15", "queued", ""],
        ]
    }
    fake_svc = _make_fake_service(get_response=fake_data)

    import scripts.sheets_helper as helper
    monkeypatch.setattr(helper, "_build_service", lambda: fake_svc)
    monkeypatch.setattr(sys, "argv", [
        "sheets_helper.py", "delete",
        "--question", "Why does X happen?",
    ])

    with pytest.raises(SystemExit) as exc:
        helper.main()
    assert exc.value.code == 0

    # batchUpdate must have been called with deleteDimension
    batch_call = fake_svc.spreadsheets.return_value.batchUpdate
    batch_call.assert_called_once()
    body = batch_call.call_args[1]["body"]
    requests = body["requests"]
    assert len(requests) == 1
    del_req = requests[0]["deleteDimension"]["range"]
    assert del_req["sheetId"] == 0  # matches fake spreadsheet_meta in _make_fake_service
    assert del_req["dimension"] == "ROWS"
    # row 2 → startIndex=1, endIndex=2 (0-based)
    assert del_req["startIndex"] == 1
    assert del_req["endIndex"] == 2

    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["question"] == "Why does X happen?"
    assert result["deleted_row"] == 2


# ---------------------------------------------------------------------------
# Test 4 — delete exits with code 2 when no match found
# ---------------------------------------------------------------------------

def test_delete_no_match_exits_2(monkeypatch, capsys):
    fake_data = {
        "values": [
            ["question", "domain", "est_minutes", "status", "date_sent"],
            ["Why is the sky blue?", "Nature & weather", "15", "queued", ""],
        ]
    }
    fake_svc = _make_fake_service(get_response=fake_data)

    import scripts.sheets_helper as helper
    monkeypatch.setattr(helper, "_build_service", lambda: fake_svc)
    monkeypatch.setattr(sys, "argv", [
        "sheets_helper.py", "delete",
        "--question", "Why does X happen?",
    ])

    with pytest.raises(SystemExit) as exc:
        helper.main()
    assert exc.value.code == 2

    captured = capsys.readouterr()
    err = json.loads(captured.err)
    assert err["error"] == "no match"


# ---------------------------------------------------------------------------
# Test 5 — delete exits with code 3 when multiple matches found
# ---------------------------------------------------------------------------

def test_delete_multiple_matches_exits_3(monkeypatch, capsys):
    fake_data = {
        "values": [
            ["question", "domain", "est_minutes", "status", "date_sent"],
            ["Duplicate question?", "The body", "15", "queued", ""],
            ["Duplicate question?", "The body", "15", "queued", ""],
        ]
    }
    fake_svc = _make_fake_service(get_response=fake_data)

    import scripts.sheets_helper as helper
    monkeypatch.setattr(helper, "_build_service", lambda: fake_svc)
    monkeypatch.setattr(sys, "argv", [
        "sheets_helper.py", "delete",
        "--question", "Duplicate question?",
    ])

    with pytest.raises(SystemExit) as exc:
        helper.main()
    assert exc.value.code == 3

    captured = capsys.readouterr()
    err = json.loads(captured.err)
    assert err["error"] == "multiple matches"
    assert len(err["rows"]) == 2


# ---------------------------------------------------------------------------
# Test 6 — missing credentials file produces helpful error message
# ---------------------------------------------------------------------------

def test_missing_credentials_exits_nonzero(monkeypatch, capsys, tmp_path):
    import scripts.sheets_helper as helper
    # Point CREDENTIALS_PATH to a path that definitely does not exist
    monkeypatch.setattr(helper, "CREDENTIALS_PATH", str(tmp_path / "no-such-file.json"))
    monkeypatch.setattr(sys, "argv", ["sheets_helper.py", "read"])

    with pytest.raises(SystemExit) as exc:
        helper.main()
    assert exc.value.code != 0

    captured = capsys.readouterr()
    # Error must name the missing path
    assert ".secrets/service-account.json" in captured.err or str(tmp_path / "no-such-file.json") in captured.err
