#!/usr/bin/env python3
"""Run the flow matrix against the real lin binary."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path("/tmp/lin-dogfood")
FIX = ROOT / "fixtures"


def _lin(home: Path, args: list[str]) -> dict[str, object]:
    env = os.environ.copy()
    env["LIN_HOME"] = str(home)
    env["PYTHONPATH"] = str(ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "lin.cli.main", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {
            "ok": False,
            "error_type": "parse_error",
            "error": result.stdout,
            "stderr": result.stderr,
        }
    if not isinstance(payload, dict):
        payload = {"ok": False, "error_type": "parse_error", "error": "stdout was not an object"}
    payload["_exit"] = result.returncode
    return payload


def _prepare(yes: bool) -> list[str]:
    args = [
        "prepare",
        "ada-north",
        "--name",
        "Ada North",
        "--day",
        "2026-06-03",
        "--lead",
        str(FIX / "lead_pass.json"),
        "--json",
    ]
    if yes:
        args.insert(-1, "--yes")
    return args


def main() -> int:
    home = OUT / "home"
    home.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, list[str], str]] = [
        ("instruct", ["instruct", "--json"], "ok"),
        ("doctor", ["doctor", "--json"], "ok"),
        ("note", ["note", "--name", "Ada North", "--json"], "ok"),
        ("score_pass", ["score", "--fixture", str(FIX / "lead_pass.json"), "--json"], "ok"),
        ("score_medspa", ["score", "--fixture", str(FIX / "lead_medspa.json"), "--json"], "fail"),
        (
            "who",
            ["who", "Ada North", "--bench", str(FIX / "bench_two.json"), "--json"],
            "ambiguous",
        ),
        ("prepare_no_yes", _prepare(False), "validation_error"),
        ("prepare_yes", _prepare(True), "stop"),
        ("send_no_yes", ["send", "ada-north", "--note", "Hi", "--json"], "validation_error"),
        ("send_yes", ["send", "ada-north", "--note", "Hi", "--yes", "--json"], "unsupported"),
        ("reply", ["reply", "--json"], "validation_error"),
        ("inmail", ["inmail", "--json"], "validation_error"),
    ]
    failed = 0
    OUT.mkdir(parents=True, exist_ok=True)
    for name, args, expect in rows:
        payload = _lin(home, args)
        (OUT / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        data = payload.get("data")
        if expect == "ok":
            good = payload.get("ok") is True
        elif expect == "fail":
            good = (
                payload.get("ok") is True
                and isinstance(data, dict)
                and data.get("passed") is False
            )
        elif expect == "stop":
            good = (
                payload.get("ok") is True
                and isinstance(data, dict)
                and data.get("stopped_before_send") is True
            )
        else:
            good = payload.get("error_type") == expect
        mark = "ok" if good else "FAIL"
        print(f"{mark} {name} exit={payload.get('_exit')} type={payload.get('error_type')}")
        failed += 0 if good else 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
