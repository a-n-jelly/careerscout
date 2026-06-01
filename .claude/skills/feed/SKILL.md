---
name: feed
description: >-
  Daily job feed scoring. Use when the user runs /feed or asks to score
  today's roles. Reads today.json, scores against targeting criteria, and
  writes feed/daily-feed-output.md. Do not use for assessing a specific role
  — that's /assess.
---

# /feed — Daily Job Feed

## What this skill does

**Goal:** Surface roles worth your time today. Not rank everything — decide what's worth seeing.

**Trigger:** Run `/feed` in Claude Code after fetch.py has populated `feed-agent/today.json`.

**Inputs:**

- `feed-agent/today.json` — roles surviving pre-filter (non-PM roles, international locations, known B2B companies, and learnings-matched patterns already removed by `filter_roles.py`)
- `feed-agent/pre_filtered.json` — roles removed by pre-filter (exists if filter_roles.py ran); used only for the skipped count in the output header
- `context/sources.md` — target companies, domain preferences, avoid list, location, comp band
- `context/differentiators.md` — your edges; used directly for Edge scoring
- `context/state.md` — pipeline roles already in progress (skip these)
- `feed-agent/learnings.md` — rejected patterns and injected roles (already applied by filter_roles.py; check for any new entries not yet caught)

**Do not load:** `resume.md`, `profile.md`, or `storybank.md`. Those belong in `/assess`.

**Outputs:**

- `feed/daily-feed-output.md` — scored shortlist, written and ready to read
- `feed-agent/dismissed.json` — updated with today's scored roles so they don't resurface

**Done when:** `feed/daily-feed-output.md` exists, is dated today, and `dismissed.json` is updated.

---

## Step 1 — Freshness check

Load `feed-agent/today.json`. Compare the `fetched_date` field against today's date.

If they don't match: **stop immediately.** Say so and ask whether to trigger `fetch.py` first. Do not score stale data.

If they match: check whether `feed-agent/pre_filtered.json` exists. If it does, note its length — this is the pre-filter count to include in the output header. If it doesn't exist (filter_roles.py hasn't run), proceed normally; the skipped count will only reflect Claude's own scoring decisions.

---

## Step 2 — Archive previous feed

Archive current `feed/daily-feed-output.md` to `feed/archive/YYYY-MM-DD.md` using today's date.

Skip if it's the placeholder ("No feed run yet").

---

## Step 3 — Extract key requirements per role

`enrich.py` runs before this step and pre-fetches descriptions from Greenhouse and Lever APIs, writing them into `today.json`. Trust that output — do not re-fetch what enrich.py already retrieved.

For each role that passes initial filtering:

- If `description` is non-empty: extract the top 4–5 **candidate requirements** — what the candidate must bring, not what the job will involve. Look for sections labelled "Qualifications", "Requirements", "What we're looking for", "What you'll bring", "Minimum qualifications", "Basic qualifications", "Who you are." Extract from those sections only. Do **not** pull from "Responsibilities", "What you'll do", "Key responsibilities", or "About the role" sections.
- If `description_available` is `false` (LinkedIn-only roles enrich.py couldn't reach): write "Requirements not available — open link to review." Do not WebFetch. **Still score the role** — use title and company context for the Requirements dimension; default to 2 unless the title signals a clear gap.
- If `description` is empty and `description_available` is not `false` (Ashby roles or any edge case enrich.py skipped): attempt one WebFetch. If it returns no content, write "Requirements not available — open link to review." **Still score the role** using title and company context.

---

## Step 4 — Score each role

Read `context/differentiators.md` before scoring. Edge scoring uses it directly.

Score each role on four dimensions (0–3 each, total 0–12):

**Match (0–3)** — domain fit against `## Domain Preferences` in `context/sources.md`.

- Proven = 3 · Adjacent = 2 · Curious = 1 · Hard no = 0 (skip immediately)
- If the domain isn't explicitly listed, use judgment based on closest category.
- Score on role type, not company name or industry label.

**Requirements (0–3)** — does the candidate meet stated requirements?

- 3 = meets core requirements · 2 = minor gap, mostly qualified · 1 = clear domain gap · 0 = disqualifying requirement
- Pure skills judgment — level is handled by thresholds below, do not double-penalize it here.

**Edge (0–3)** — do the differentiators in `context/differentiators.md` give a specific advantage?

- Use the "Notes for scoring" section in that file.

**Sustain (0–3)** — location first, then comp.

- Location is a hard gate: if the role doesn't match location criteria in `context/sources.md` → Sustain = 0, full stop.
- If location passes, score comp on the **upper end of the posted range**:
  - Upper ≥ target AND lower ≥ floor = 3
  - Upper ≥ target but lower below floor (wide range) = 2
  - Upper ≥ floor but below target = 1
  - Upper below floor = 0
  - Comp not listed = 1 · No location data = 0

**Recommend thresholds — use the `level` field from today.json:**

| Level | Standard | Priority Company [TARGET] |
|-------|----------|--------------------------|
| `target` | ≥ 7 AND Sustain ≥ 1 | ≥ 6 AND Sustain ≥ 1 |
| `above_target` | ≥ 9 AND Sustain ≥ 1 | ≥ 6 AND Sustain ≥ 1 |
| `below_target` | Skip immediately | Skip immediately |

Tag `above_target` roles `[ABOVE LEVEL]`. Tag Priority Company roles `[TARGET]`. Both tags can appear together.

**Skip immediately (do not score) if:** matches avoid list · already in pipeline · matches a rejected pattern in `learnings.md`.

**Injected roles** (`injected: true`) always appear in Recommended with the reason they were added.

---

## Step 5 — Write feed/daily-feed-output.md

```markdown
# Job Feed — [DATE]

[N recommended] · [N stretch] · [N skipped] ([N pre-filtered] auto-removed before scoring)

**Fit scoring:** Match (domain fit) / Requirements (stated requirements met) / Edge (differentiator advantage) / Sustain (comp + location). Each 0–3, total 0–12. Target-level roles recommend at ≥7; Priority Companies [TARGET] at ≥6. Above-level roles appear in Stretch only.

---

## Recommended

### [Role Title] — [Company] [TARGET] [REPOST]
- **Fit score:** Match [N] / Requirements [N] / Edge [N] / Sustain [N] = [total]/12
- **Why this is yours:** [one sentence referencing a specific differentiator — not generic language]
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
- **Why this is yours:** [one sentence referencing a specific differentiator — not generic language]
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

## Step 6 — Update dismissed.json

Write all scored role IDs (Recommended and Stretch) to `feed-agent/dismissed.json`:

```json
{
  "[id]": {"title": "[role title]", "company": "[company]", "dismissed_date": "[YYYY-MM-DD]"}
}
```

Merge with existing entries — do not overwrite. `fetch.py` reads this on the next run to skip already-seen roles.

To bring a role back: remove its ID from `dismissed.json` or run `/feed add`.

---

## Step 7 — Calibration nudge

Count archived feeds in `feed/archive/` to determine run number.

**Runs 1–4:** End with:

> "This is run [N] — the first few feeds usually have noise. Run `/feed-review` to work through the list, then `/calibrate` if anything felt systematically off. Watch for: wrong domain, level mismatches, companies you'd never consider, comp scores that don't match your expectations."

Append to `feed/daily-feed-output.md`:

```
---
Run [N] of your feed. Run `/feed-review` to work through the list — then `/calibrate` if you spot patterns worth fixing.
```

**Run 5+:** End with:

> "Run `/feed-review` to work through the list. Run `/calibrate` if something felt off."

Append to `feed/daily-feed-output.md`:

```
---
Run `/feed-review` to work through the list. Run `/calibrate` if something felt systematically off.
```

---

## Rules

- One sentence per role in the skipped list. This is a scan, not a review.
- Do not surface roles already in `state.md`.
- If `today.json` is empty or missing, say so and stop.
- American spellings throughout.
