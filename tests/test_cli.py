"""Real CLI subprocess. No LinkedIn calls."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"


def _run(home: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["LIN_HOME"] = str(home)
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "lin.cli.main", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _json(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    payload = json.loads(result.stdout)
    assert isinstance(payload, dict)
    return payload


def test_instruct_doctor_note(tmp_path: Path) -> None:
    recipe = _json(_run(tmp_path, "instruct", "--json"))
    assert recipe["ok"] is True
    doctor = _json(_run(tmp_path, "doctor", "--json"))
    assert isinstance(doctor["data"], dict)
    assert doctor["data"]["sends"] is False
    note = _json(_run(tmp_path, "note", "--name", "Ada North", "--json"))
    assert isinstance(note["data"], dict)
    assert note["data"]["chars"] <= 300


def test_score_and_who(tmp_path: Path) -> None:
    passed = _json(_run(tmp_path, "score", "--fixture", str(FIX / "lead_pass.json"), "--json"))
    assert isinstance(passed["data"], dict)
    assert passed["data"]["passed"] is True
    missed = _json(_run(tmp_path, "score", "--fixture", str(FIX / "lead_medspa.json"), "--json"))
    assert isinstance(missed["data"], dict)
    assert missed["data"]["passed"] is False
    ambiguous = _json(
        _run(tmp_path, "who", "Ada North", "--bench", str(FIX / "bench_two.json"), "--json")
    )
    assert ambiguous["error_type"] == "ambiguous"
    assert isinstance(ambiguous["candidates"], list)
    assert len(ambiguous["candidates"]) == 2


def test_prepare_requires_yes_and_stops(tmp_path: Path) -> None:
    refused = _json(
        _run(
            tmp_path,
            "prepare",
            "ada-north",
            "--name",
            "Ada North",
            "--day",
            "2026-06-03",
            "--json",
        )
    )
    assert refused["error_type"] == "validation_error"
    assert not (tmp_path / "invites.jsonl").exists()
    ready = _json(
        _run(
            tmp_path,
            "prepare",
            "ada-north",
            "--name",
            "Ada North",
            "--day",
            "2026-06-03",
            "--yes",
            "--lead",
            str(FIX / "lead_pass.json"),
            "--json",
        )
    )
    assert ready["ok"] is True
    assert isinstance(ready["data"], dict)
    assert ready["data"]["stopped_before_send"] is True
    assert not (tmp_path / "invites.jsonl").exists()


def test_send_reply_and_log(tmp_path: Path) -> None:
    no_yes = _json(_run(tmp_path, "send", "ada-north", "--note", "Hi", "--json"))
    assert no_yes["error_type"] == "validation_error"
    blocked = _json(_run(tmp_path, "send", "ada-north", "--note", "Hi", "--yes", "--json"))
    assert blocked["error_type"] == "unsupported"
    assert "human_fix" in blocked
    reply = _json(_run(tmp_path, "reply", "--json"))
    assert reply["error_type"] == "validation_error"
    logged = _json(
        _run(tmp_path, "log", "ada-north", "--day", "2026-06-03", "--yes", "--json")
    )
    assert logged["ok"] is True
    again = _json(
        _run(tmp_path, "log", "ada-north", "--day", "2026-06-03", "--yes", "--json")
    )
    assert isinstance(again["data"], dict)
    assert again["data"]["logged"] == 1


def test_login_hides_the_cookie(tmp_path: Path) -> None:
    secret = "cookie-do-not-print"
    login = _run(tmp_path, "login", "--cookie", secret, "--json")
    assert secret not in login.stdout
    assert secret not in login.stderr
    mode = (tmp_path / "session.json").stat().st_mode
    assert stat.S_IMODE(mode) == 0o600
    doctor = _json(_run(tmp_path, "doctor", "--json"))
    assert secret not in json.dumps(doctor)
    assert isinstance(doctor["data"], dict)
    assert doctor["data"]["session_mode_ok"] is True
