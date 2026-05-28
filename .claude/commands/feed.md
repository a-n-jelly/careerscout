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

**Freshness check:** After loading today.json, compare the `fetched_date` field against today's date. If they don't match, stop immediately and say so — don't run the feed on stale data. Ask whether to trigger fetch.py first.

---

## Step 2 — Archive previous feed

Archive current `feed/feed.md` to `feed/archive/YYYY-MM-DD.md` using today's date.
Skip if it's the placeholder ("No feed run yet").

---

## Step 2.5 — Extract key requirements per role

`enrich.py` runs before this step and pre-fetches descriptions from Greenhouse and Lever APIs, writing them into today.json. Trust that output — do not re-fetch what enrich.py already retrieved.

For each role that passes initial filtering:

- If `description` is non-empty: extract the top 4-5 requirements directly from the description text. This covers Indeed, LinkedIn-with-description, and all Greenhouse/Lever roles enriched by enrich.py.
- If `description_available` is `false` (LinkedIn-only roles enrich.py couldn't reach): write "Requirements not available — open link to review." Do not WebFetch.
- If `description` is empty and `description_available` is not `false` (Ashby roles, or any edge case enrich.py skipped): attempt one WebFetch. If it returns no content, write "Requirements not available — open link to review."

---

## Step 3 — Score each role

Read `context/differentiators.md` before scoring. Edge scoring uses it directly.

Score each role on four dimensions (0–3 each). Total 0–12.

- **Match (0–3)** — is this the right domain? Consumer-facing fintech, payments, lending, regulated environment. Score on role signals only, not company name.

- **Requirements (0–3)** — does the candidate meet the stated requirements? Pure domain and skills judgment — level is handled by the thresholds below, do not double-penalise it here. 3 = meets core requirements. 2 = minor gap, mostly qualified. 1 = clear domain gap. 0 = disqualifying requirement they don't have.

- **Edge (0–3)** — do the differentiators in `context/differentiators.md` give a specific advantage for this role? Use the "Notes for scoring" section in that file.

- **Sustain (0–3)** — location first, then comp. Location is a hard gate: if the role doesn't match the user's location criteria in `context/sources.md` (city, remote preference, relocation) — Sustain = 0, full stop, regardless of comp. If location passes, score comp on the **upper end of the posted range** (read comp band from `context/sources.md`): upper end ≥ target AND lower end ≥ floor = 3. Upper end ≥ target but lower end below floor (wide range) = 2. Upper end ≥ floor but below target = 1. Upper end below floor = 0. Comp not listed = 1. No location data = 0.

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

Check how many archived feeds exist in `feed/archive/`. Count = number of prior runs.

**Runs 1–4 (early):** The feed is still learning. End with a specific nudge in the conversational response:

> "This is run [N] — the first few feeds usually have noise. After you've read through it, run `/feed-review` to work through the list, then `/calibrate` if anything felt systematically off. Things to watch for: roles in the wrong domain, level mismatches, companies you'd never consider, comp scores that don't match your expectations."

Also append to feed.md:
```
---
Run [N] of your feed. Run `/feed-review` to work through the list — then `/calibrate` if you spot patterns worth fixing (wrong domain, level mismatches, companies to exclude).
```

**Run 5+ (mature):** End with the standard nudge:

> "Run `/feed-review` to work through the list. Run `/calibrate` if something felt off."

Also append to feed.md:
```
---
Run `/feed-review` to work through the list. Run `/calibrate` if something felt systematically off.
```

---

## Rules

- One sentence per role. This is a scan.
- Do not surface roles already in state.md.
- If today.json is empty or missing, say so and stop.
- British spellings throughout.
