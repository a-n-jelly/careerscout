#!/usr/bin/env python3
"""
filter_roles.py — Fast pre-filter before enrichment and scoring.

Removes clearly out-of-scope roles based on title, location, and company so
Claude only scores viable candidates. Runs after filter_dismissed.py, before
enrich.py.

Writes:
  - today.json        (in place, surviving roles only)
  - pre_filtered.json (filtered roles + reason, used by /feed for skipped section)
"""

import json
import re
from pathlib import Path

FEED_AGENT = Path(__file__).parent
BASE       = FEED_AGENT.parent
TODAY      = FEED_AGENT / "today.json"
FILTERED   = FEED_AGENT / "pre_filtered.json"
LEARNINGS  = FEED_AGENT / "learnings.md"
SOURCES    = BASE / "context" / "sources.md"

# ── Non-PM role patterns ──────────────────────────────────────────────────────
# Matched against the full lowercase title. Any hit → not a PM role, skip.

NON_PM_TITLE_PATTERNS = [
    r"\bsoftware (development )?engineer\b",
    r"\bsde\b",
    r"\bengineering manager\b",
    r"\bsales development\b",              # catches both "Sales Development Manager" and "Manager, Sales Development"
    r"\bbusiness development (representative|manager)\b",
    r"\bpartner development (manager|lead)\b",
    r"\blearning (and|&) development\b",
    r"\btalent (and|&) development\b",
    r"\bchange enablement\b",
    r"\bfacilitator\b",
    r"\brecruiter\b",
    r"\bdata scientist\b",
    r"\bsolutions architect\b",
    r"\baccount (executive|manager)\b",
    r"\bbusiness analyst\b",
    r"\bbranded merchandise\b",
    r"\bpolicy development\b",
    r"\bprogram/product manager\b",
    r"\bstaff (software|data|ml|ai) engineer\b",
    r"\bsolutions business development\b",
    r"\bintern\b",                         # intern roles
    r"\bspecialist\b.*\bproduct manager\b|\bproduct manager\b.*\bspecialist\b",  # "CRO Specialist / Product Manager"
    r"\bbusiness development partner\b",
]

# ── International location patterns ──────────────────────────────────────────
# Matched against the lowercase location field. Any hit → location gate fails.

INTL_LOCATION_PATTERNS = [
    r"\bunited kingdom\b", r"\buk\b(?!\s*-\s*remote)",
    r"\blondon\b",
    r"\bireland\b", r"\bdublin\b",
    r"\bgermany\b", r"\bnederlands\b", r"\bnetherlands\b",
    r"\bsingapore\b",
    r"\btokyo\b", r"\bjapan\b",
    r"\bsydney\b", r"\baustralia\b",
    r"\bbangkok\b", r"\bthailand\b",
    r"\bindia\b", r"\bbengaluru\b", r"\bbangalore\b",
    r"\bcanada\b", r"\btoronto\b", r"\bvancouver\b",
    r"\bcdmx\b", r"\bmexico\b",
    r"\bemea\b",
    r"remote.*canada",
    r"remote.*emea",
]

# ── Hard-no title keyword patterns ───────────────────────────────────────────
# High-confidence role-type signals. Only applied to PM/product roles that
# passed the non-PM filter above. Each entry is (pattern, reason).

HARD_NO_TITLE_PATTERNS = [
    (r"\bfraud\b",                                      "fraud domain"),
    (r"\btrust (and|&) safety\b",                       "fraud/trust domain"),
    (r"\benforcement systems\b",                        "trust/safety domain"),
    (r"\binfrastructure (pm|product)\b",                "infra PM"),
    (r"\b(pm|product manager)[,\s-]+infrastructure\b",  "infra PM"),
    (r"\bcompute platform\b",                           "infra PM"),
    (r"\bpayment rail\b",                               "payment rails infra"),
    (r"\breal.time payment\b",                          "payment rails infra"),
    (r"\bdata platform\b",                              "data platform PM"),
    (r"\bdata (and )?internal products\b",              "data platform PM"),
    (r"\bdata center\b",                                "hardware/data center"),
    (r"\bwarehouse management\b",                       "logistics/ops"),
    (r"\bsourcing and procurement\b",                   "internal ops tooling"),
    (r"\bmerchandise planning\b",                       "internal ops tooling"),
    (r"\bobservabilit\b",                               "developer observability"),
    (r"\bmonitoring\b.*\bpm\b|\bpm\b.*\bmonitoring\b", "developer observability"),
    (r"\bdevops\b",                                     "developer tooling"),
    (r"\bgrowth ai outreach\b",                         "growth/acquisition"),
    (r"\bblood culture\b",                              "medical devices"),
    (r"\basset health\b",                               "IoT/ops"),
    (r"\bclaim adjudication\b",                         "healthcare admin"),
    (r"\bprovider data management\b",                   "healthcare admin"),
    (r"\bmedicare (enrollment|provider)\b",             "healthcare admin"),
    (r"\bcms integration\b",                            "healthcare admin"),
    (r"\bsell?ing partner\b",                           "B2B seller tooling"),
    (r"\bspecialty pharmacy\b",                         "B2B healthcare"),
    (r"\bflight connectivity\b",                        "ops/logistics"),
    (r"\bexternal services.*aws\b|\baws.*external services\b", "developer-facing APIs"),
    (r"\bprivate pricing\b",                            "B2B pricing infra"),
    (r"\bacquisitions?\b",                              "growth/acquisition PM"),
    (r"\bnpi product manager\b",                        "hardware NPI"),
    (r"\biot product manager\b",                        "IoT/hardware"),
    (r"\bunderground\b",                                "industrial/hardware"),
    (r"\bconversion rate optimization\b",               "growth/acquisition"),
    (r"\bcybersecurity\b",                              "security domain"),
    (r"\bnetwork\b.*(health|medical|clinical)",         "healthcare network B2B"),
    (r"\blangsmith\b|\blangchain\b",                    "developer tooling"),
    (r"\bfintechs (and|&) exchanges\b",                 "crypto/exchange infra"),
    (r"\blast mile delivery\b",                         "logistics/ops"),
    (r"\bctv\b",                                        "adtech"),
    (r"\bsalesforce (and|&) internal\b",                "internal B2B tooling"),
    (r"\bplatform (services|infrastructure)\b",         "infra/platform PM"),
    (r"\bpersonalization (and|&) discovery\b",          "ML/recommendation systems gap"),
    (r"\bmachine learning\b.*\bpm\b|\bpm\b.*\bmachine learning\b", "ML product gap"),
    (r"\benvironmental.*(senior |)product manager\b",   "industrial/env domain"),
]

# ── Known B2B/enterprise company skip list ───────────────────────────────────
# Companies whose entire product suite is B2B enterprise — any PM role they
# post will be enterprise SaaS. Add to this list after repeated skips.
# Case-insensitive substring match against role["company"].

B2B_COMPANY_SKIP_LIST = [
    # Industrial / manufacturing / hardware — no plausible PM role overlap
    "raytheon",
    "lincoln electric",
    "g&w electric",
    "standard motor products",
    "fluke corporation",
    "sick ",           # SICK AG industrial sensors (trailing space avoids false matches)
    "picarro",
    "buspatrol",
    "lineage",         # temperature-controlled warehousing
    # Pure enterprise IT infrastructure — no consumer surface
    "veeam",
    "grafana labs",
    # Healthcare admin / claims — requires deep domain expertise we don't have
    "healthedge",
    "navitus",
    "enlyte",
    "pointclickcare",
    # Defence / government / clearance required
    "trajector",       # VA disability benefits
    # Staffing agencies posting opaque roles
    "hollstadt",
    "talently",
    "cyberobotix",
]

# Short company names that need exact/word-boundary matching (substring match too broad)
B2B_COMPANY_EXACT = {"f5", "sap", "bd"}  # case-insensitive full company name match

# ── Learnings-based filter ────────────────────────────────────────────────────

def load_rejected_patterns():
    """
    Parse learnings.md ## Rejected section into (company, [keywords]) pairs.

    Lines look like:
      - [YYYY-MM-DD] Company — Role title — reason | signal:...

    Extracts meaningful keywords (4+ chars, not stopwords) from the role title.
    Matching requires company substring match AND all keywords present in title.
    This handles learnings titles like "Senior PM, Card Experience" matching
    actual titles like "Senior Product Manager, Card Experience".
    """
    if not LEARNINGS.exists():
        return []

    STOPWORDS = {
        "senior", "staff", "lead", "principal", "manager", "product",
        "the", "and", "of", "for", "in", "a", "an", "to", "new", "with"
    }

    patterns = []
    in_rejected = False
    for line in LEARNINGS.read_text().splitlines():
        stripped = line.strip()
        if stripped == "## Rejected":
            in_rejected = True
            continue
        if stripped.startswith("## ") and in_rejected:
            break
        if not in_rejected or not stripped.startswith("- ["):
            continue
        m = re.match(r"- \[\d{4}-\d{2}-\d{2}\] (.+?) — (.+?) —", stripped)
        if m:
            company  = m.group(1).strip().lower()
            raw_title = m.group(2).strip().lower()
            keywords = [
                re.sub(r"[^a-z0-9]", "", w)
                for w in raw_title.split()
                if len(w.strip(",.;:")) >= 4 and w.strip(",.;:") not in STOPWORDS
            ]
            keywords = [k for k in keywords if k]  # drop empty after stripping
            if company and keywords:
                patterns.append((company, keywords))
    return patterns


def matches_rejected_pattern(role, rejected_patterns):
    company = role.get("company", "").lower()
    title   = role.get("title", "").lower()
    title_clean = re.sub(r"[^a-z0-9 ]", "", title)
    for pat_company, keywords in rejected_patterns:
        if pat_company not in company:
            continue
        if all(kw in title_clean for kw in keywords):
            return f"rejected pattern ({', '.join(keywords[:3])})"
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def matches_any(text, patterns):
    """Return the first matching pattern string, or None."""
    t = text.lower()
    for p in patterns:
        if re.search(p, t):
            return p
    return None


def is_non_pm(title):
    return matches_any(title, NON_PM_TITLE_PATTERNS)


def is_international(location):
    if not location or str(location).strip() in ("", "nan"):
        return None
    return matches_any(location, INTL_LOCATION_PATTERNS)


def is_hard_no_domain(title):
    t = title.lower()
    for pattern, reason in HARD_NO_TITLE_PATTERNS:
        if re.search(pattern, t):
            return reason
    return None


def is_b2b_company(company):
    if not company or str(company).strip() in ("", "nan"):
        return None
    c = company.lower().strip()
    # Exact match for short names (avoids "bd" matching "adobe", "f5" matching "f5 networks" substring issues)
    for name in B2B_COMPANY_EXACT:
        if c == name or c.startswith(name + " ") or c.endswith(" " + name):
            return f"known B2B company ({name})"
    # Substring match for longer names
    for name in B2B_COMPANY_SKIP_LIST:
        if name.strip() in c:
            return f"known B2B company ({name.strip()})"
    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def load_comp_floor():
    """Parse comp floor from sources.md. Returns floor as int (USD) or None."""
    if not SOURCES.exists():
        return None
    for line in SOURCES.read_text().splitlines():
        m = re.search(r"\$(\d+)K?\s+floor", line)
        if m:
            val = int(m.group(1))
            return val * 1000 if val < 10000 else val
    return None


def is_below_comp_floor(role, floor):
    """
    Returns reason string if the upper end of the comp range is below the floor.
    Uses the 'compensation' field populated by fetch.py (_format_comp).
    Only filters when there is a posted range AND the upper end is below floor.
    """
    if not floor:
        return None
    comp = str(role.get("compensation") or "").strip()
    if not comp:
        return None

    # Extract all dollar amounts from the string (handles "$140K–$180K", "$75/hr", etc.)
    amounts = []
    for m in re.finditer(r"\$(\d+(?:\.\d+)?)(K)?", comp):
        val = float(m.group(1))
        if m.group(2):          # K suffix
            val *= 1000
        if "/hr" in comp:       # hourly — annualise at 2080 hrs
            val *= 2080
        amounts.append(val)

    if not amounts:
        return None

    upper = max(amounts)
    if upper < floor:
        return f"comp upper ${upper/1000:.0f}K below floor ${floor//1000}K"
    return None


def main():
    if not TODAY.exists():
        print("today.json not found — nothing to filter")
        raise SystemExit(0)

    roles = json.loads(TODAY.read_text())
    rejected_patterns = load_rejected_patterns()
    comp_floor = load_comp_floor()
    before = len(roles)

    surviving = []
    filtered  = []  # list of {title, company, location, url, reason}

    for role in roles:
        title    = str(role.get("title", "") or "")
        company  = str(role.get("company", "") or "")
        location = str(role.get("location", "") or "")

        # 1. Non-PM role?
        if is_non_pm(title):
            filtered.append({**role, "_filter_reason": "not a PM role"})
            continue

        # 2. International location?
        reason = is_international(location)
        if reason:
            filtered.append({**role, "_filter_reason": "international location"})
            continue

        # 3. Matches a previously rejected pattern from learnings.md?
        reason = matches_rejected_pattern(role, rejected_patterns)
        if reason:
            filtered.append({**role, "_filter_reason": reason})
            continue

        # 4. Hard-no domain signal in title?
        reason = is_hard_no_domain(title)
        if reason:
            filtered.append({**role, "_filter_reason": reason})
            continue

        # 5. Known B2B company?
        reason = is_b2b_company(company)
        if reason:
            filtered.append({**role, "_filter_reason": reason})
            continue

        # 6. Comp posted and upper end below floor?
        reason = is_below_comp_floor(role, comp_floor)
        if reason:
            filtered.append({**role, "_filter_reason": reason})
            continue

        surviving.append(role)

    # Write filtered list for /feed skipped section
    FILTERED.write_text(json.dumps(filtered, indent=2))

    # Write surviving roles back in place
    TODAY.write_text(json.dumps(surviving, indent=2))

    # Summary
    by_reason = {}
    for r in filtered:
        key = r["_filter_reason"]
        by_reason[key] = by_reason.get(key, 0) + 1

    print(f"Pre-filter: {before} → {len(surviving)} roles ({before - len(surviving)} removed)")
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        print(f"  {count:3d}  {reason}")


if __name__ == "__main__":
    main()
