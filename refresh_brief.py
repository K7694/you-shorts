#!/usr/bin/env python3
"""
Refreshes the Analyzer brief only if it's stale (>20 hours old) or missing.
Called from the GitHub Actions workflow before the main pipeline, so the
brief stays fresh without burning YouTube API quota on every single run.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BRIEF = Path("analyzer/latest_brief.json")
MAX_AGE_HOURS = 20


def main() -> int:
    needs_refresh = True
    if BRIEF.exists():
        try:
            data = json.loads(BRIEF.read_text(encoding="utf-8"))
            age = (datetime.now() - datetime.fromisoformat(data["generated"])).total_seconds() / 3600
            needs_refresh = age > MAX_AGE_HOURS
            status = "STALE — refreshing" if needs_refresh else "fresh — skipping"
            print(f"Brief age: {age:.1f}hrs — {status}")
        except Exception as e:
            print(f"Brief unreadable ({e}) — refreshing")
    else:
        print("No brief found — generating fresh")

    if not needs_refresh:
        return 0

    print("Running analyzer.py to regenerate brief...")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run([sys.executable, "analyzer.py"], check=False, env=env)
    if result.returncode != 0:
        print(f"Analyzer exited with code {result.returncode} — pipeline will fall back")
    return 0  # Never block the pipeline — it has its own fallback


if __name__ == "__main__":
    sys.exit(main())
