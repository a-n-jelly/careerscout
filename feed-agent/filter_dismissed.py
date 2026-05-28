#!/usr/bin/env python3
"""
filter_dismissed.py — Remove previously seen roles from today.json before enrichment.

Runs after fetch.py, before enrich.py. Roles in dismissed.json were already
surfaced and reviewed — no point enriching or scoring them again.
"""

import json
from pathlib import Path

FEED_AGENT = Path(__file__).parent
TODAY = FEED_AGENT / "today.json"
DISMISSED = FEED_AGENT / "dismissed.json"

if not TODAY.exists():
    print("today.json not found — nothing to filter")
    raise SystemExit(0)

roles = json.loads(TODAY.read_text())
dismissed = set(json.loads(DISMISSED.read_text()).keys()) if DISMISSED.exists() else set()

before = len(roles)
roles = [r for r in roles if r["id"] not in dismissed]
after = len(roles)

TODAY.write_text(json.dumps(roles, indent=2))
print(f"Dismissed filter: {before - after} removed ({after} remaining for enrichment and scoring)")
