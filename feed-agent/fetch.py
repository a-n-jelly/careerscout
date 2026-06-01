#!/usr/bin/env python3
"""
feed-agent/fetch.py — Daily job fetch engine

Reads sources.md → runs JobSpy → hits ATS endpoints → dedupes → writes today.json
Run from career-coach/ root: python3 feed-agent/fetch.py
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

BASE       = Path(__file__).parent.parent   # career-coach/
FEED_AGENT = Path(__file__).parent          # career-coach/feed-agent/
SOURCES      = BASE / "context" / "sources.md"
LEARNINGS    = FEED_AGENT / "learnings.md"
SEEN_JSON    = FEED_AGENT / "seen.json"
DISMISSED_JSON = FEED_AGENT / "dismissed.json"
TODAY_JSON   = FEED_AGENT / "today.json"

STAFFING_AGENCIES = {
    "akkodis", "spectraforce", "impax recruitment", "hays", "robert half",
    "kforce", "insight global", "teksystems", "cybercoders", "hired",
    "jobgether", "lancesoft", "staffmark", "apex systems",
}


# ── Parsers ──────────────────────────────────────────────────────────────────

def parse_sources():
    text = SOURCES.read_text()
    section = None

    queries        = []
    avoid_rules    = []   # list of {"logic": "any"|"all", "keywords": [...]}
    target_companies = []
    ats_map        = {}
    title_keywords = ["product manager", "pm"]   # defaults
    level_config   = {
        "target":       ["senior", "sr", "staff", "lead", "principal"],
        "above_target": ["director", "vp", "head of", "vice president", "chief"],
        "below_target": ["associate", "junior", "jr", "entry level", "pm i", "pm1"],
    }
    location_config = {
        "primary":      "",
        "accept_remote": True,
        "reject_cities": [],
    }
    feed_settings = {"results_wanted": 15, "hours_old": 72}

    for line in text.splitlines():
        stripped = line.strip()

        if stripped.startswith("## "):
            section = stripped[3:].lower().strip()
            continue

        # Search queries
        if section == "search queries (run these)" and re.match(r"^\d+\.", stripped):
            q = re.sub(r"^\d+\.\s*", "", stripped).strip()
            if q:
                queries.append(q)

        # Feed settings
        elif section == "feed settings":
            m = re.match(r"results_wanted:\s*(\d+)", stripped)
            if m:
                feed_settings["results_wanted"] = int(m.group(1))
            m = re.match(r"hours_old:\s*(\d+)", stripped)
            if m:
                feed_settings["hours_old"] = int(m.group(1))

        # Target titles
        elif section == "target titles" and stripped.startswith("-"):
            kw = stripped.lstrip("- ").strip().lower()
            if kw:
                title_keywords.append(kw)

        # Target level
        elif section == "target level" and stripped.startswith("**"):
            m = re.match(r"\*\*(.*?)\*\*[:\s]+(.*)", stripped)
            if m:
                label = m.group(1).lower().strip()
                keywords = [k.strip().lower() for k in m.group(2).split(",")]
                if "above" in label:
                    level_config["above_target"] = keywords
                elif "below" in label:
                    level_config["below_target"] = keywords
                elif "target" in label:
                    level_config["target"] = keywords

        # Location
        elif section == "location":
            m = re.match(r"\*\*primary city\*\*[:\s]+(.*)", stripped, re.IGNORECASE)
            if m:
                location_config["primary"] = m.group(1).strip()
            m = re.match(r"\*\*accept remote\*\*[:\s]+(.*)", stripped, re.IGNORECASE)
            if m:
                location_config["accept_remote"] = "yes" in m.group(1).lower()
            m = re.match(r"\*\*reject if clearly located in\*\*[:\s]+(.*)", stripped, re.IGNORECASE)
            if m:
                cities = [c.strip().lower() for c in m.group(1).split(",") if c.strip()]
                location_config["reject_cities"] = cities

        # Priority companies
        elif section == "priority companies" and "|" in stripped:
            if stripped.startswith("|-") or "company" in stripped.lower():
                continue
            parts = [p.strip() for p in stripped.split("|") if p.strip()]
            if parts:
                target_companies.append(parts[0])

        # ATS endpoints
        elif section == "ats endpoints" and "|" in stripped:
            if stripped.startswith("|-") or "company" in stripped.lower():
                continue
            parts = [p.strip() for p in stripped.split("|") if p.strip()]
            if len(parts) >= 3:
                ats_map[parts[0]] = {"type": parts[1].lower(), "slug": parts[2]}

        # What to avoid
        elif section == "what to avoid" and stripped.startswith("-"):
            rule = stripped.lstrip("- ").strip().lower()
            if not rule or rule.startswith("["):
                continue
            if rule.startswith("and:"):
                keywords = rule[4:].strip().split()
                avoid_rules.append({"logic": "all", "keywords": keywords})
            else:
                avoid_rules.append({"logic": "any", "keywords": [rule]})

    # Dedupe title_keywords
    title_keywords = list(dict.fromkeys(title_keywords))

    return {
        "queries":          queries,
        "avoid_rules":      avoid_rules,
        "target_companies": target_companies,
        "ats":              ats_map,
        "title_keywords":   title_keywords,
        "level_config":     level_config,
        "location_config":  location_config,
        "feed_settings":    feed_settings,
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


# ── Filters ───────────────────────────────────────────────────────────────────

PLACEHOLDER_LOCATIONS = {"add all locations here", "add location here", "tbd", "various"}


def location_acceptable(job_location: str, location_config: dict) -> bool:
    loc = (job_location or "").lower()
    if not loc or loc in ("nan", "none", ""):
        return True  # No location data — let scorer handle via Sustain 0
    if any(p in loc for p in PLACEHOLDER_LOCATIONS):
        return True  # Placeholder — Sustain 0 at scoring

    primary = location_config.get("primary", "").lower()
    accept_remote = location_config.get("accept_remote", True)
    reject_cities = location_config.get("reject_cities", [])

    # Check primary city match
    if primary:
        primary_words = [w for w in primary.replace(",", " ").split() if len(w) > 1]
        if any(w in loc for w in primary_words):
            return True

    # Check remote indicators
    remote_indicators = {"remote", "united states", "us", "usa", "anywhere"}
    if accept_remote and any(r in loc for r in remote_indicators):
        # Exclude explicitly rejected cities
        if reject_cities and any(city in loc for city in reject_cities):
            return False
        return True

    # If we have a primary city and nothing matched, reject
    if primary:
        return False

    return True


def is_target_title(title: str, title_keywords: list) -> bool:
    title_lower = title.lower()
    return any(kw in title_lower for kw in title_keywords)


def classify_level(title: str, level_config: dict) -> str:
    title_lower = title.lower()
    for kw in level_config.get("above_target", []):
        if kw in title_lower:
            return "above_target"
    for kw in level_config.get("below_target", []):
        if kw in title_lower:
            return "below_target"
    return "target"


def should_avoid(job: dict, avoid_rules: list) -> tuple:
    text = f"{job['title']} {job.get('description', '')}".lower()

    for rule in avoid_rules:
        keywords = rule["keywords"]
        logic = rule["logic"]
        if logic == "any" and any(k in text for k in keywords):
            return True, " ".join(keywords)
        if logic == "all" and all(k in text for k in keywords):
            return True, " ".join(keywords)

    # Always filter staffing agencies regardless of sources.md
    company_lower = job.get("company", "").lower()
    if any(agency in company_lower for agency in STAFFING_AGENCIES):
        return True, "staffing-agency"

    return False, None


def matches_rejected(job, rejected):
    text = f"{job['title']} {job['company']} {job.get('description', '')}".lower()
    for pattern in rejected:
        words = [w for w in pattern.split()[:4] if len(w) > 3]
        if words and all(w in text for w in words):
            return True
    return False


# ── Helpers ──────────────────────────────────────────────────────────────────

def _format_comp(row):
    """Format JobSpy salary fields into a human-readable string, or return ''."""
    try:
        lo  = row.get("min_amount")
        hi  = row.get("max_amount")
        interval = str(row.get("interval") or "").lower()

        if not lo and not hi:
            return ""

        def fmt(n):
            if n is None:
                return None
            n = float(n)
            if interval in ("hourly", "hour"):
                return f"${n:.0f}/hr"
            # Convert hourly that slipped through as yearly
            return f"${n/1000:.0f}K" if n >= 1000 else f"${n:.0f}"

        lo_s = fmt(lo)
        hi_s = fmt(hi)

        if lo_s and hi_s:
            return f"{lo_s}–{hi_s}"
        return lo_s or hi_s or ""
    except Exception:
        return ""


# ── Fetch ─────────────────────────────────────────────────────────────────────

def run_jobspy(query, location_config, feed_settings):
    primary = location_config.get("primary", "")
    q_lower = query.lower()

    # Infer search location from query or primary city config
    if primary and any(w in q_lower for w in primary.lower().split()):
        location = primary
    elif "remote" in q_lower:
        location = "United States"
    elif primary:
        location = primary
    else:
        location = "United States"

    try:
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "glassdoor", "zip_recruiter", "google"],
            search_term=query,
            location=location,
            results_wanted=feed_settings.get("results_wanted", 15),
            hours_old=feed_settings.get("hours_old", 72),
        )
        results = []
        for _, row in jobs.iterrows():
            job_loc = str(row.get("location", "") or "")
            if not location_acceptable(job_loc, location_config):
                continue
            results.append({
                "title":       str(row.get("title", "") or ""),
                "company":     str(row.get("company", "") or ""),
                "location":    job_loc,
                "url":         str(row.get("job_url", "") or ""),
                "description": str(row.get("description", "") or "")[:3000],
                "source":      str(row.get("site", "") or ""),
                "date_posted": str(row.get("date_posted", "") or ""),
                "compensation": _format_comp(row),
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
            data = fetch_url(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
            return [{
                "title":       j.get("title", ""),
                "company":     company,
                "location":    j.get("location", {}).get("name", ""),
                "url":         j.get("absolute_url", ""),
                "description": "",
                "source":      "greenhouse",
                "date_posted": (j.get("updated_at", "") or "")[:10],
            } for j in data.get("jobs", [])]

        elif ats_type == "lever":
            data = fetch_url(f"https://api.lever.co/v0/postings/{slug}")
            return [{
                "title":       j.get("text", ""),
                "company":     company,
                "location":    j.get("categories", {}).get("location", ""),
                "url":         j.get("hostedUrl", ""),
                "description": "",
                "source":      "lever",
                "date_posted": "",
            } for j in data]

        elif ats_type == "ashby":
            data = fetch_url(f"https://api.ashbyhq.com/posting-api/job-board/{slug}")
            return [{
                "title":       j.get("title", ""),
                "company":     company,
                "location":    j.get("locationName", ""),
                "url":         j.get("jobPostingUrl", ""),
                "description": "",
                "source":      "ashby",
                "date_posted": (j.get("publishedDate", "") or "")[:10],
            } for j in data.get("jobPostings", [])]

    except (urllib.error.URLError, json.JSONDecodeError, Exception) as e:
        print(f"    ATS error for {company}: {e}")

    return []


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    today = str(date.today())
    print(f"Job Feed Fetch — {today}")
    print("=" * 40)

    sources   = parse_sources()
    learnings = parse_learnings()
    seen      = load_seen()
    dismissed = load_dismissed()

    location_config = sources["location_config"]
    level_config    = sources["level_config"]
    title_keywords  = sources["title_keywords"]
    avoid_rules     = sources["avoid_rules"]
    feed_settings   = sources["feed_settings"]

    print(f"Queries: {len(sources['queries'])}  |  Target companies: {len(sources['target_companies'])}")
    print(f"ATS endpoints: {len(sources['ats'])}  |  Avoid rules: {len(avoid_rules)}")
    print(f"Rejected patterns: {len(learnings['rejected'])}  |  Dismissed: {len(dismissed)}")
    print(f"Location: {location_config.get('primary') or 'not set'}  |  Remote: {location_config.get('accept_remote')}")

    raw = []

    print("\nJobSpy searches:")
    for q in sources["queries"]:
        print(f"  → {q[:70]}")
        results = run_jobspy(q, location_config, feed_settings)
        print(f"     {len(results)} raw")
        raw.extend(results)

    if sources["ats"]:
        print("\nATS endpoints:")
        for company, info in sources["ats"].items():
            print(f"  → {company} ({info['type']})")
            results = fetch_ats(company, info)
            print(f"     {len(results)} results")
            raw.extend(results)

    print(f"\nTotal raw: {len(raw)}")

    # Description-aware dedup: same title+company → keep entry with longest description
    best_by_role: dict = {}
    for job in raw:
        key = f"{job.get('title', '').lower().strip()}|{job.get('company', '').lower().strip()}"
        existing = best_by_role.get(key)
        if not existing or len(job.get("description", "") or "") > len(existing.get("description", "") or ""):
            best_by_role[key] = job
    raw = list(best_by_role.values())
    print(f"After description-aware dedup: {len(raw)}")

    # Filter + dedup
    filtered  = []
    seen_ids  = set()
    stats     = {"not_pm": 0, "avoided": 0, "rejected": 0, "dupes": 0, "reposts": 0, "below_level": 0}
    target_set = {c.lower() for c in sources["target_companies"]}

    for job in raw:
        if not job.get("title") or not job.get("company"):
            continue

        h = job_hash(job["title"], job["company"], job.get("url", ""))

        if h in seen_ids:
            stats["dupes"] += 1
            continue
        seen_ids.add(h)

        # Title filter
        if not is_target_title(job["title"], title_keywords):
            stats["not_pm"] += 1
            continue

        # Level filter — skip below target
        level = classify_level(job["title"], level_config)
        if level == "below_target":
            stats["below_level"] += 1
            continue

        avoided, _ = should_avoid(job, avoid_rules)
        if avoided:
            stats["avoided"] += 1
            continue

        if matches_rejected(job, learnings["rejected"]):
            stats["rejected"] += 1
            continue

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
            "id":           h,
            "repost":       repost,
            "is_target":    is_target,
            "level":        level,
            "fetched_date": today,
            "injected":     False,
        })

        if not repost:
            seen[h] = {"title": job["title"], "company": job["company"], "date": today}

    # Injected roles from learnings
    for entry in learnings["injected"]:
        parts = [p.strip() for p in entry.split("—")]
        if len(parts) >= 2:
            company_part = parts[0].split()[-1] if parts[0].split() else ""
            role = parts[1] if len(parts) > 1 else ""
            if company_part and role:
                h = job_hash(role, company_part)
                filtered.append({
                    "title": role, "company": company_part, "location": "",
                    "url": "", "description": "", "source": "manual",
                    "date_posted": "", "id": h, "repost": False,
                    "is_target": True, "level": "target",
                    "fetched_date": today, "injected": True,
                })

    TODAY_JSON.write_text(json.dumps(filtered, indent=2))
    save_seen(seen)

    print(f"\nFilter stats:")
    print(f"  Not a target title    : {stats['not_pm']}")
    print(f"  Below target level    : {stats['below_level']}")
    print(f"  Avoided (criteria)    : {stats['avoided']}")
    print(f"  Rejected (learnings)  : {stats['rejected']}")
    print(f"  Dupes (within run)    : {stats['dupes']}")
    print(f"  Reposts (flagged)     : {stats['reposts']}")
    print(f"\nWrote {len(filtered)} roles → today.json")
    print(f"Seen index: {len(seen)} total")


if __name__ == "__main__":
    main()
