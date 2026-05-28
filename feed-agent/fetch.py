#!/usr/bin/env python3
"""
feed-agent/fetch.py — Daily job fetch engine

Reads sources.md → runs JobSpy → hits ATS endpoints → dedupes → writes today.json
Run from job-agent/ root: python3 feed-agent/fetch.py
"""

import json
import hashlib
import re
import ssl
import sys
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

try:
    from jobspy import scrape_jobs
except ImportError:
    print("ERROR: python-jobspy not installed. Run: pip install python-jobspy")
    sys.exit(1)

BASE = Path(__file__).parent.parent          # job-agent/
FEED_AGENT = Path(__file__).parent           # job-agent/feed-agent/
SOURCES = BASE / "context" / "sources.md"
LEARNINGS = FEED_AGENT / "learnings.md"
SEEN_JSON = FEED_AGENT / "seen.json"
DISMISSED_JSON = FEED_AGENT / "dismissed.json"
TODAY_JSON = FEED_AGENT / "today.json"


# ── Parsers ──────────────────────────────────────────────────────────────────

def parse_sources():
    text = SOURCES.read_text()
    queries, avoid, target_companies, ats_map = [], [], [], {}

    section = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].lower()
            continue

        if section == "search queries (run these)" and re.match(r"^\d+\.", stripped):
            q = re.sub(r"^\d+\.\s*", "", stripped)
            if q:
                queries.append(q)

        elif section == "avoid" and stripped.startswith("-"):
            avoid.append(stripped.lstrip("- ").lower())

        elif section == "priority companies" and stripped and not stripped.startswith("#"):
            for c in re.split(r",\s*", stripped):
                c = c.strip()
                # Skip prose lines — company names don't contain spaces beyond "Cash App"
                if c and len(c.split()) <= 2 and not c.startswith("Roles"):
                    target_companies.append(c)

        elif section == "ats endpoints" and "|" in stripped:
            if stripped.startswith("|-") or "company" in stripped.lower():
                continue
            parts = [p.strip() for p in stripped.split("|") if p.strip()]
            if len(parts) >= 3:
                ats_map[parts[0]] = {"type": parts[1].lower(), "slug": parts[2]}

    return {
        "queries": queries,
        "avoid": avoid,
        "target_companies": target_companies,
        "ats": ats_map,
    }


def parse_learnings():
    if not LEARNINGS.exists():
        return {"rejected": [], "injected": []}

    text = LEARNINGS.read_text()
    rejected, injected, section = [], [], None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            section = stripped[3:].lower()
        elif section == "rejected" and stripped.startswith("-"):
            rejected.append(stripped.lstrip("- ").lower())
        elif section == "injected" and stripped.startswith("-"):
            injected.append(stripped.lstrip("- "))

    return {"rejected": rejected, "injected": injected}


# ── Dedup ─────────────────────────────────────────────────────────────────────

def job_hash(title, company, url=""):
    key = f"{title.lower().strip()}|{company.lower().strip()}|{url}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def load_seen():
    if not SEEN_JSON.exists():
        return {}
    return json.loads(SEEN_JSON.read_text())


def save_seen(seen):
    SEEN_JSON.write_text(json.dumps(seen, indent=2))


def load_dismissed():
    if not DISMISSED_JSON.exists():
        return {}
    return json.loads(DISMISSED_JSON.read_text())


# ── Fetch ─────────────────────────────────────────────────────────────────────

SEATTLE_STATES = {"wa", "washington", "seattle"}
VALID_REMOTE_INDICATORS = {"remote", "united states", "us", "usa", "anywhere"}
PLACEHOLDER_LOCATIONS = {"add all locations here", "add location here", "tbd", "various"}


def location_acceptable(job_location: str, query_type: str) -> bool:
    """Return False if the role's location clearly doesn't match the query type."""
    loc = (job_location or "").lower()
    if not loc or loc in ("nan", "none", ""):
        return True  # No location data — let the scorer handle via Sustain 0
    if any(p in loc for p in PLACEHOLDER_LOCATIONS):
        return True  # Placeholder location — Sustain 0 at scoring stage

    if query_type == "seattle":
        # Must contain Seattle or WA, or be remote
        return any(s in loc for s in SEATTLE_STATES) or any(r in loc for r in VALID_REMOTE_INDICATORS)

    if query_type == "remote":
        # Must not be a specific non-Seattle city
        # Reject if it contains a known non-Seattle city indicator
        reject_locations = ["cleveland", "new york", "ny,", " ny ", "chicago",
                            "boston", "austin", "dallas", "atlanta", "denver",
                            "white plains", "charlotte", "phoenix", "miami"]
        return not any(r in loc for r in reject_locations)

    return True


def run_jobspy(query):
    q_lower = query.lower()
    if "seattle" in q_lower:
        location = "Seattle, WA"
        query_type = "seattle"
    elif "remote" in q_lower:
        location = "United States"
        query_type = "remote"
    else:
        location = "United States"
        query_type = "remote"

    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "glassdoor", "zip_recruiter", "google"],
            search_term=query,
            location=location,
            results_wanted=15,
            hours_old=72,
        )
        results = []
        for _, row in jobs.iterrows():
            job_loc = str(row.get("location", "") or "")
            if not location_acceptable(job_loc, query_type):
                continue
            results.append({
                "title": str(row.get("title", "") or ""),
                "company": str(row.get("company", "") or ""),
                "location": job_loc,
                "url": str(row.get("job_url", "") or ""),
                "description": str(row.get("description", "") or "")[:1000],
                "source": str(row.get("site", "") or ""),
                "date_posted": str(row.get("date_posted", "") or ""),
            })
        return results
    except Exception as e:
        print(f"    JobSpy error: {e}")
        return []


def fetch_ats(company, ats_info):
    ats_type = ats_info.get("type", "")
    slug = ats_info.get("slug", "")
    if not slug:
        return []

    def fetch_url(url):
        return json.loads(urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}),
            timeout=10,
            context=SSL_CONTEXT,
        ).read())

    try:
        if ats_type == "greenhouse":
            url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
            data = fetch_url(url)
            return [
                {
                    "title": j.get("title", ""),
                    "company": company,
                    "location": j.get("location", {}).get("name", ""),
                    "url": j.get("absolute_url", ""),
                    "description": "",
                    "source": "greenhouse",
                    "date_posted": (j.get("updated_at", "") or "")[:10],
                }
                for j in data.get("jobs", [])
            ]

        elif ats_type == "lever":
            url = f"https://api.lever.co/v0/postings/{slug}"
            data = fetch_url(url)
            return [
                {
                    "title": j.get("text", ""),
                    "company": company,
                    "location": j.get("categories", {}).get("location", ""),
                    "url": j.get("hostedUrl", ""),
                    "description": "",
                    "source": "lever",
                    "date_posted": "",
                }
                for j in data
            ]

        elif ats_type == "ashby":
            url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
            data = fetch_url(url)
            return [
                {
                    "title": j.get("title", ""),
                    "company": company,
                    "location": j.get("locationName", ""),
                    "url": j.get("jobPostingUrl", ""),
                    "description": "",
                    "source": "ashby",
                    "date_posted": (j.get("publishedDate", "") or "")[:10],
                }
                for j in data.get("jobPostings", [])
            ]

    except (urllib.error.URLError, json.JSONDecodeError, Exception) as e:
        print(f"    ATS error for {company}: {e}")

    return []


# ── Filters ───────────────────────────────────────────────────────────────────

_PM_RE = re.compile(r'\b(product\s+manager|sr\.?\s*pm|senior\s+pm)\b', re.IGNORECASE)
_SENIOR_RE = re.compile(r'\b(senior|sr\.?|staff|principal|lead)\b', re.IGNORECASE)
_ABOVE_VP_RE = re.compile(r'\b(director|vp\b|vice\s+president|head\s+of|chief|executive|president)\b', re.IGNORECASE)
_JUNIOR_RE = re.compile(r'\b(associate|entry.level|junior|jr\.?)\b', re.IGNORECASE)


def is_senior_pm(title):
    if not _PM_RE.search(title):
        return False
    if not _SENIOR_RE.search(title):
        return False
    if _ABOVE_VP_RE.search(title):
        return False
    if _JUNIOR_RE.search(title):
        return False
    return True


_ABOVE_TARGET_RE = re.compile(
    r'\b(principal|staff|director|vp\b|vice\s+president|head\s+of|chief)\b', re.IGNORECASE
)
_BELOW_TARGET_RE = re.compile(
    r'\b(associate|junior|jr\.?|entry.level|\bpm\s+i\b|\bpm1\b)\b', re.IGNORECASE
)


def classify_level(title):
    """Returns 'above_target', 'below_target', or 'target'."""
    if _ABOVE_TARGET_RE.search(title):
        return "above_target"
    if _BELOW_TARGET_RE.search(title):
        return "below_target"
    return "target"


# (logic, keywords, reason): "any" = OR match, "all" = AND match
AVOID_RULES = [
    ("any", ["supply chain", "supplier enablement", "logistics", "healthcare",
             "edtech", "ed tech", "clinical", "medical", "retail ops"], "out-of-domain"),
    ("all", ["platform", "infrastructure"], "platform-infra"),
    ("any", ["growth pm", "growth product manager"], "growth-pm"),
    ("all", ["enterprise", "b2b"], "enterprise-saas"),
    ("any", ["visa sponsorship", "work authorization required", "sponsorship required"], "sponsorship"),
]

# Staffing agencies and recruiters — never direct hires
STAFFING_AGENCIES = {
    "akkodis", "spectraforce", "impax recruitment", "hays", "robert half",
    "kforce", "insight global", "teksystems", "cybercoders", "hired",
    "jobgether", "lancesoft", "staffmark", "apex systems",
}


def should_avoid(job):
    text = f"{job['title']} {job['description']}".lower()
    for logic, keywords, reason in AVOID_RULES:
        if logic == "any" and any(k in text for k in keywords):
            return True, reason
        if logic == "all" and all(k in text for k in keywords):
            return True, reason

    # Filter staffing agencies
    company_lower = job.get("company", "").lower()
    if any(agency in company_lower for agency in STAFFING_AGENCIES):
        return True, "staffing-agency"

    return False, None


def matches_rejected(job, rejected):
    text = f"{job['title']} {job['company']} {job['description']}".lower()
    for pattern in rejected:
        words = [w for w in pattern.split()[:4] if len(w) > 3]
        if words and all(w in text for w in words):
            return True
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = str(date.today())
    print(f"Job Feed Fetch — {today}")
    print("=" * 40)

    sources = parse_sources()
    learnings = parse_learnings()
    seen = load_seen()
    dismissed = load_dismissed()

    print(f"Queries: {len(sources['queries'])}  |  Target companies: {len(sources['target_companies'])}")
    print(f"ATS endpoints: {len(sources['ats'])}  |  Rejected patterns: {len(learnings['rejected'])}")
    print(f"Dismissed (seen in feed): {len(dismissed)}")

    raw = []

    # JobSpy searches
    print("\nJobSpy searches:")
    for q in sources["queries"]:
        print(f"  → {q[:70]}")
        results = run_jobspy(q)
        print(f"     {len(results)} raw")
        raw.extend(results)

    # ATS endpoint fetches
    if sources["ats"]:
        print("\nATS endpoints:")
        for company, info in sources["ats"].items():
            print(f"  → {company} ({info['type']})")
            results = fetch_ats(company, info)
            print(f"     {len(results)} results")
            raw.extend(results)

    print(f"\nTotal raw: {len(raw)}")

    # Description-aware dedup: for same title+company across sources,
    # keep the entry with the longest description (prefer LinkedIn/Indeed over ATS)
    best_by_role: dict = {}
    for job in raw:
        key = f"{job.get('title', '').lower().strip()}|{job.get('company', '').lower().strip()}"
        existing = best_by_role.get(key)
        if not existing or len(job.get("description", "") or "") > len(existing.get("description", "") or ""):
            best_by_role[key] = job
    raw = list(best_by_role.values())
    print(f"After description-aware dedup: {len(raw)}")

    # Filter + dedup
    filtered = []
    seen_ids = set()
    stats = {"not_pm": 0, "avoided": 0, "rejected": 0, "dupes": 0, "reposts": 0}
    target_set = {c.lower() for c in sources["target_companies"]}

    for job in raw:
        if not job.get("title") or not job.get("company"):
            continue

        h = job_hash(job["title"], job["company"], job.get("url", ""))

        # Within-run dedupe
        if h in seen_ids:
            stats["dupes"] += 1
            continue
        seen_ids.add(h)

        # Level/domain filter
        if not is_senior_pm(job["title"]):
            stats["not_pm"] += 1
            continue

        avoided, _ = should_avoid(job)
        if avoided:
            stats["avoided"] += 1
            continue

        if matches_rejected(job, learnings["rejected"]):
            stats["rejected"] += 1
            continue

        # Skip roles the user has already seen in the feed
        if h in dismissed:
            stats["reposts"] += 1
            continue

        repost = h in seen
        if repost:
            stats["reposts"] += 1

        is_target = any(
            tc in job["company"].lower() or job["company"].lower() in tc
            for tc in target_set
        )

        filtered.append({
            **job,
            "id": h,
            "repost": repost,
            "is_target": is_target,
            "level": classify_level(job["title"]),
            "fetched_date": today,
            "injected": False,
        })

        if not repost:
            seen[h] = {"title": job["title"], "company": job["company"], "date": today}

    # Injected roles from learnings
    for entry in learnings["injected"]:
        # Format: [date] Company — Role — reason
        parts = [p.strip() for p in entry.split("—")]
        if len(parts) >= 2:
            company_part = parts[0].split()[-1] if parts[0].split() else ""
            role = parts[1] if len(parts) > 1 else ""
            if company_part and role:
                h = job_hash(role, company_part)
                filtered.append({
                    "title": role,
                    "company": company_part,
                    "location": "",
                    "url": "",
                    "description": "",
                    "source": "manual",
                    "date_posted": "",
                    "id": h,
                    "repost": False,
                    "is_target": True,
                    "fetched_date": today,
                    "injected": True,
                })

    TODAY_JSON.write_text(json.dumps(filtered, indent=2))
    save_seen(seen)

    print(f"\nFilter stats:")
    print(f"  Not a senior PM title : {stats['not_pm']}")
    print(f"  Avoided (criteria)    : {stats['avoided']}")
    print(f"  Rejected (learnings)  : {stats['rejected']}")
    print(f"  Dupes (within run)    : {stats['dupes']}")
    print(f"  Reposts (flagged)     : {stats['reposts']}")
    print(f"\nWrote {len(filtered)} roles → today.json")
    print(f"Seen index: {len(seen)} total")


if __name__ == "__main__":
    main()
