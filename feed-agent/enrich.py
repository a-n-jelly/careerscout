#!/usr/bin/env python3
"""
feed-agent/enrich.py — Description enrichment step

Runs after fetch.py, before /feed scoring. Reads today.json (~50 filtered roles),
adds full job descriptions where missing, then writes back in place.

What it does:
  - LinkedIn dedup: if (title, company) exists in Indeed/ATS, drop LinkedIn and keep
    the description-bearing source. If LinkedIn-only, keep with description_available=False.
  - Greenhouse: fetch full JD from boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}
  - Lever: fetch full JD from api.lever.co/v0/postings/{slug}/{posting_id}
  - Indeed / other JobSpy sources: already have description from fetch.py, skip
  - Ashby: no stable individual posting API — left as-is (description stays empty)

Run from CareerScout/ root: python3 feed-agent/enrich.py
"""

import html as html_module
import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from collections import defaultdict
from pathlib import Path

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

BASE = Path(__file__).parent.parent
FEED_AGENT = Path(__file__).parent
TODAY_JSON = FEED_AGENT / "today.json"
SOURCES = BASE / "context" / "sources.md"

# More generous than fetch.py's 1000 — scorer benefits from reading actual requirements
DESCRIPTION_LIMIT = 3000


# ── Helpers ───────────────────────────────────────────────────────────────────

def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=10, context=SSL_CONTEXT).read()
    return json.loads(raw)


def strip_html(raw):
    """Decode HTML entities, strip tags, normalise whitespace.

    Greenhouse returns entity-encoded content (&lt;div&gt;...) so entities
    must be decoded before the tag-stripping regex runs.
    """
    if not raw:
        return ""
    text = html_module.unescape(raw)        # &lt; → <, &amp; → &, etc.
    text = re.sub(r"<[^>]+>", " ", text)   # strip actual HTML tags
    return re.sub(r"\s+", " ", text).strip()


def load_greenhouse_slugs():
    """Parse sources.md ATS table and return {company_lower: slug} for Greenhouse entries."""
    if not SOURCES.exists():
        return {}
    slugs = {}
    in_ats_section = False
    for line in SOURCES.read_text().splitlines():
        stripped = line.strip()
        if stripped.startswith("## ") and "ats endpoints" in stripped.lower():
            in_ats_section = True
            continue
        if stripped.startswith("## ") and in_ats_section:
            break  # left the ATS section
        if in_ats_section and "|" in stripped:
            if stripped.startswith("|-") or "company" in stripped.lower():
                continue
            parts = [p.strip() for p in stripped.split("|") if p.strip()]
            if len(parts) >= 3 and parts[1].lower() == "greenhouse":
                slugs[parts[0].lower()] = parts[2]
    return slugs


def dedup_key(role):
    return (role["title"].lower().strip(), role["company"].lower().strip())


# ── LinkedIn dedup ─────────────────────────────────────────────────────────────

def dedup_linkedin(roles):
    """
    For each (title, company) group:
      - If a non-LinkedIn version exists: use that, drop LinkedIn duplicate(s).
      - If LinkedIn-only: keep it, set description_available=False.

    Returns (deduplicated_list, n_dropped).
    """
    groups = defaultdict(list)
    for role in roles:
        groups[dedup_key(role)].append(role)

    result = []
    dropped = 0

    for group in groups.values():
        linkedin = [r for r in group if r.get("source") == "linkedin"]
        other    = [r for r in group if r.get("source") != "linkedin"]

        if not linkedin:
            # No LinkedIn in this group — keep as-is
            result.extend(other)
        elif other:
            # Prefer description-bearing non-LinkedIn source(s); drop LinkedIn
            result.extend(other)
            dropped += len(linkedin)
        else:
            # LinkedIn-only — keep one copy, flag it
            kept = linkedin[0]
            kept["description_available"] = False
            result.append(kept)

    return result, dropped


# ── Source-specific enrichment ────────────────────────────────────────────────

def enrich_greenhouse(role, slug_map):
    """
    Extract slug + job_id from the role URL, fetch full JD, strip HTML.

    Handles two URL patterns:
      Standard : https://boards.greenhouse.io/{slug}/jobs/{job_id}
      Custom   : https://{company}.com/...?gh_jid={job_id}
                 (Stripe, SoFi, etc. use their own domain; slug comes from sources.md)

    Returns True if description was populated.
    """
    job_url = role.get("url", "")
    slug, job_id = None, None

    # Pattern 1: boards.greenhouse.io/{slug}/jobs/{job_id}
    m = re.search(r"boards\.greenhouse\.io/([^/?]+)/jobs/(\d+)", job_url)
    if m:
        slug, job_id = m.group(1), m.group(2)

    # Pattern 2: ?gh_jid={job_id} — look up slug from sources.md ATS map
    if not slug:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(job_url).query)
        gh_jid = qs.get("gh_jid", [None])[0]
        if gh_jid:
            job_id = gh_jid
            slug = slug_map.get(role.get("company", "").lower())

    if not slug or not job_id:
        return False

    api_url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs/{job_id}"
    try:
        data = fetch_json(api_url)
        html = data.get("content", "") or ""
        role["description"] = strip_html(html)[:DESCRIPTION_LIMIT]
        return bool(role["description"])
    except (urllib.error.URLError, json.JSONDecodeError, Exception) as e:
        print(f"      ✗ Greenhouse fetch failed: {e}")
        return False


def enrich_lever(role):
    """
    Extract slug + posting_id from URL, fetch full JD.
    Lever URL pattern: https://jobs.lever.co/{slug}/{posting_id}
    API endpoint: https://api.lever.co/v0/postings/{slug}/{posting_id}
    Returns True if description was populated.
    """
    m = re.search(r"jobs\.lever\.co/([^/?]+)/([^/?]+)", role["url"])
    if not m:
        return False

    slug, posting_id = m.group(1), m.group(2)
    url = f"https://api.lever.co/v0/postings/{slug}/{posting_id}"

    try:
        data = fetch_json(url)
        # Prefer plain text; fall back to stripping HTML
        plain = data.get("descriptionPlain", "")
        if not plain:
            plain = strip_html(data.get("description", ""))
        # Append additional section if present (often has requirements)
        additional = data.get("additionalPlain", "") or strip_html(data.get("additional", ""))
        combined = (plain + " " + additional).strip() if additional else plain
        role["description"] = combined[:DESCRIPTION_LIMIT]
        return bool(role["description"])
    except (urllib.error.URLError, json.JSONDecodeError, Exception) as e:
        print(f"      ✗ Lever fetch failed: {e}")
        return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TODAY_JSON.exists():
        print("ERROR: today.json not found — run fetch.py first.")
        sys.exit(1)

    roles = json.loads(TODAY_JSON.read_text())
    slug_map = load_greenhouse_slugs()

    print(f"Enrich — {len(roles)} roles loaded from today.json")
    print(f"Greenhouse slug map: {len(slug_map)} companies")
    print("=" * 40)

    # Step 1: LinkedIn dedup
    roles, dropped = dedup_linkedin(roles)
    print(f"LinkedIn dedup: {dropped} dropped (replaced by description-bearing source)")

    # Step 2: Identify what needs enrichment
    to_enrich = [
        r for r in roles
        if not r.get("description")
        and r.get("source") in ("greenhouse", "lever")
        and r.get("description_available") is not False  # already flagged → skip
    ]

    n_greenhouse = sum(1 for r in to_enrich if r["source"] == "greenhouse")
    n_lever      = sum(1 for r in to_enrich if r["source"] == "lever")
    n_already    = sum(1 for r in roles if r.get("description"))
    n_no_desc    = sum(1 for r in roles if r.get("description_available") is False)

    print(f"Already have description : {n_already}")
    print(f"Need enrichment          : {len(to_enrich)} ({n_greenhouse} Greenhouse, {n_lever} Lever)")
    print(f"LinkedIn-only (no JD)    : {n_no_desc}")

    if to_enrich:
        print()

    enriched = 0
    failed   = 0

    for i, role in enumerate(to_enrich):
        src = role["source"]
        label = f"[{i+1}/{len(to_enrich)}]"
        print(f"  {label} {src.capitalize()}: {role['company']} — {role['title'][:55]}")

        if src == "greenhouse":
            ok = enrich_greenhouse(role, slug_map)
        elif src == "lever":
            ok = enrich_lever(role)
        else:
            ok = False

        if ok:
            enriched += 1
            snippet = role["description"][:80].replace("\n", " ")
            print(f"      ✓ {len(role['description'])} chars -- \"{snippet}...\"")
        else:
            failed += 1
            role["description_available"] = False
            print(f"      – marked description_available=False")

        # Polite rate-limiting between API calls
        if i < len(to_enrich) - 1:
            time.sleep(0.35)

    # Write enriched today.json back in place
    TODAY_JSON.write_text(json.dumps(roles, indent=2))

    print(f"\nEnrichment complete:")
    print(f"  Descriptions fetched : {enriched}")
    print(f"  Failed / no URL      : {failed}")
    print(f"  LinkedIn-only (no JD): {n_no_desc + failed}")
    print(f"  Total roles          : {len(roles)}")


if __name__ == "__main__":
    main()
