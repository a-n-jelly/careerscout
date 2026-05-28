> **Purpose:** Your search criteria for the daily job feed. fetch.py reads this file to know what to fetch, filter, and score. Only needed if you're using the feed agent.

# Job Feed — Search Criteria

---

## Search Queries (run these)

One search per line. Include location signal in the query if needed (e.g. "Senior PM fintech Seattle").

1. [e.g. Senior Product Manager fintech Seattle]
2. [e.g. Senior PM payments remote]
3. [e.g. Senior Product Manager consumer tech Seattle]

---

## Feed Settings

```
results_wanted: 15
hours_old: 72
```

---

## Target Titles

A role title must contain at least one of these to pass the title filter. Case-insensitive.

- product manager
- pm

---

## Target Level

fetch.py uses these to classify roles as target, above-target (Stretch), or below-target (Skip).

**Target:** senior, sr, staff, lead, principal
**Above target:** director, vp, head of, vice president, chief
**Below target:** associate, junior, jr, entry level, pm i, pm1

---

## Location

**Primary city:** [e.g. Seattle, WA]
**Accept remote:** yes
**Reject if clearly located in:** [comma-separated cities to exclude from remote results, e.g. New York, Chicago, Boston, Austin, Atlanta, Denver]

---

## Priority Companies

Companies worth watching directly — feed scores these more generously.

| Company | Why |
|---------|-----|
| [Company] | [One-line reason] |

---

## ATS Endpoints

Direct ATS feeds for priority companies. Supported types: greenhouse, lever, ashby.

| Company | Type | Slug |
|---------|------|------|
| [Company] | greenhouse | [slug] |

---

## What to Avoid

One rule per line. fetch.py skips any role where the title or description matches.
Use `AND:` prefix to require all words to match (default is any word matches).

- staffing agencies
- [domain to exclude, e.g. healthcare]
- [role type to exclude, e.g. growth pm]
- AND: [word1] [word2] (e.g. AND: platform infrastructure)
