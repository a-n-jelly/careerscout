# /feed — Daily Job Feed

Scores roles from `feed-agent/today.json` against your targeting criteria and writes a shortlist to `feed/feed.md`. Lightweight — no resume, no storybank. Those belong in `/assess`.

---

## Step 1 — Load context

Read:
- `feed-agent/today.json` — roles to score
- `context/sources.md` — target companies, signals, avoid list, location, comp band, differentiators
- `context/state.md` — pipeline roles already in progress (skip these)
- `feed-agent/learnings.md` — rejected patterns and injected roles

That's it. Do not load resume.md, profile.md, or storybank.md.

---

## Step 2 — Archive previous feed

Archive current `feed/feed.md` to `feed/archive/YYYY-MM-DD.md` using today's date.
Skip if it's the placeholder ("No feed run yet").

---

## Step 2.5 — Extract key requirements per role

For each role that passes initial filtering, extract 4-5 key requirements to include in the feed output:

- If `description` is non-empty in today.json (Indeed/LinkedIn roles): extract the top 4-5 requirements directly from the description text.
- If `description` is empty (ATS roles — Greenhouse, Lever, Ashby): fetch the job URL using WebFetch with prompt "List the top 5 key requirements from this job posting as short bullet points." Cache results — don't re-fetch the same URL twice.
- If the URL is inaccessible or returns no content: write "Requirements not available — open link to review."

---

## Step 3 — Score each role

Read `context/differentiators.md` before scoring. Edge scoring uses it directly.

Score each role on four dimensions (0–3 each). Total 0–12.

- **Match (0–3)** — is this the right domain? Consumer-facing fintech, payments, lending, regulated environment. Score on role signals only, not company name.

- **Requirements (0–3)** — does the candidate meet the stated requirements? Pure domain and skills judgment — level is handled by the thresholds below, do not double-penalise it here. 3 = meets core requirements. 2 = minor gap, mostly qualified. 1 = clear domain gap. 0 = disqualifying requirement they don't have.

- **Edge (0–3)** — do the differentiators in `context/differentiators.md` give a specific advantage for this role? Use the "Notes for scoring" section in that file.

- **Sustain (0–3)** — comp + location. At/above target base = 3. At floor = 1. Below floor or no location data = 0.

**Recommend thresholds — use the `level` field from today.json:**

| Level | Standard | Priority Company [TARGET] |
|-------|----------|--------------------------|
| `target` | ≥ 7 AND Sustain ≥ 1 | ≥ 6 AND Sustain ≥ 1 |
| `above_target` | ≥ 9 AND Sustain ≥ 1 | ≥ 6 AND Sustain ≥ 1 |
| `below_target` | Skip immediately | Skip immediately |

Tag `above_target` roles with `[ABOVE LEVEL]`. Tag Priority Company roles with `[TARGET]`. Both tags can appear on the same role.

Skip immediately (do not score) if: matches avoid list, already in pipeline, matches a rejected pattern in learnings.md.

Injected roles (flagged `injected: true`) always appear in Worth a Look with the reason you added them.

---

## Step 4 — Write feed/feed.md

```markdown
# Job Feed — [DATE]

[N recommended] · [N stretch] · [N skipped]

**Fit scoring:** Match (domain fit) / Requirements (stated requirements met) / Edge (differentiator advantage) / Sustain (comp + location). Each 0–3, total 0–12. Target-level roles recommend at ≥7; Priority Companies [TARGET] at ≥6. Above-level roles appear in Stretch only.

---

## Recommended

### [Role Title] — [Company] [TARGET] [REPOST]
- **Fit score:** Match [N] / Requirements [N] / Edge [N] / Sustain [N] = [total]/12
- **Why this is yours:** [one sentence referencing a specific differentiator, not generic language]
- **Link:** [URL or "direct ATS — no link"]
- **Location:** [location] · [Remote / Hybrid / On-site]
- **Comp:** [band if listed, or "not listed"]

<details>
<summary>Key requirements</summary>

- [req 1]
- [req 2]
- [req 3]
- [req 4]
- [req 5]

</details>

---

## Stretch — Above Level

_These roles are above your current target level. Surface them if the score is strong, but don't pursue unless you're deliberately aiming up._

### [Role Title] — [Company] [TARGET] [REPOST] [ABOVE LEVEL]
- **Fit score:** Match [N] / Requirements [N] / Edge [N] / Sustain [N] = [total]/12
- **Why this is yours:** [one sentence referencing a specific differentiator, not generic language]
- **Link:** [URL or "direct ATS — no link"]
- **Location:** [location] · [Remote / Hybrid / On-site]
- **Comp:** [band if listed, or "not listed"]

<details>
<summary>Key requirements</summary>

- [req 1]
- [req 2]
- [req 3]
- [req 4]
- [req 5]

</details>

---

<details>
<summary>Skipped ([N])</summary>

### [Role Title] — [Company]
- **Why:** [which filter triggered or score that disqualified it]

</details>

---

_Fetched: [date]. Run `/assess` on any role worth a closer look._
```

---

## Step 5 — Write dismissed roles

After writing feed/feed.md, write all scored role IDs (both Recommended and
Stretch) to `feed-agent/dismissed.json`. Format:

```json
{
  "[id]": {"title": "[role title]", "company": "[company]", "dismissed_date": "[YYYY-MM-DD]"}
}
```

Merge with any existing dismissed.json — do not overwrite previous entries.
Fetch.py reads this file and skips dismissed roles on the next run, so roles
won't resurface until they're re-posted under a new ID.

To bring a role back: remove its ID from dismissed.json or use `/feed add`.

---

## Step 6 — Calibration nudge

After writing feed/feed.md, always append the following — and always surface it
prominently in the conversational response, not just in the file:

```
---
If any of these felt off, run `/calibrate` to tune the scoring, avoid list, or edge profile.
```

In the conversational response, end with: "Run `/calibrate` if any of these felt off."

---

## Rules

- One sentence per role. This is a scan.
- Do not surface roles already in state.md.
- If today.json is empty or missing, say so and stop.
- British spellings throughout.
