---
name: calibrate
description: >
  Feed calibration protocol. Use when the user runs /calibrate, says the feed
  was off, wants to tune the scoring, improve future results, or adjust the avoid
  list, target signals, comp band, or differentiator profile. Also trigger when
  the user says things like "the feed keeps surfacing the wrong roles", "the
  scores don't feel right", or "how do I make the feed better".
---

# /calibrate — Feed Calibration Protocol

Turns your reaction to the last feed into concrete changes to the config files
the scorer reads. No changes are written until you've confirmed each one.

---

## Minimum Data Check

Requires `feed/feed.md` to exist and contain scored results (not the placeholder).
If it's missing or empty: "Run `/feed` first to generate a scored feed, then come back."

---

## Step 1 — Load context

Read:
- `feed/feed.md` — most recent scored output (recommended roles + scores)
- `feed-agent/today.json` — role data including descriptions (used to surface requirements without live fetches)
- `feed-agent/learnings.md` — existing rejected patterns and injected roles
- `context/sources.md` — avoid list, target signals, priority companies, comp band
- `context/differentiators.md` — edge scoring profile

Note the feed summary: how many recommended, how many skipped, the date.

Build an in-memory lookup from today.json: `id → {description, url}`. Used in Step 3.

---

## Step 2 — Ask which mode

> "Looking at the last feed ([N] recommended, [M] skipped — [date]). Want to go
> role by role through the recommended list, or give me your overall read first?"

Don't assume. The user picks the grain.

---

## Step 3 — Collect signal

### Role-by-role mode

Pull each recommended role from `feed/feed.md` in order. For each role:

1. Look up the role in the today.json lookup by matching company + title.
2. If `description` is non-empty (Indeed/LinkedIn roles): extract and show the top 4-5 requirements inline from the description text before asking for feedback.
3. If `description` is empty (ATS roles — Greenhouse, Lever, Ashby): fetch the URL live using WebFetch with prompt "Extract the top 5 key requirements from this job posting." Only fetch if the user hasn't already said skip.
4. Then ask:

> "[Company] — [Role], [N]/12.
> Key requirements:
> - [req 1]
> - [req 2]
> - [req 3]
> Worth pursuing, or something felt off?"

Note the feedback and map it to a cause (see intent table below). Move to the
next role without writing or queuing anything yet. After all roles: "Anything
else — systematic patterns, missing companies, scores that felt structurally
wrong?"

### Overall read mode

One open question:

> "What felt off — or what worked? Anything systematic you noticed?"

Map the response to root cause using the intent table. If the cause is ambiguous,
pull specific roles to clarify:

> "This one — [Company] [Role] scored [N]/12. What felt wrong about that?"

Go role by role only until the cause is clear — not all N roles.

### Intent mapping (internal logic)

| What the user says | Likely root cause | File to fix |
|--------------------|-------------------|-------------|
| "Too many [X] type roles appearing" | Missing rejection pattern | `learnings.md` Rejected |
| "[Company] keeps showing up — I'd never apply" | Company-level rejection | `learnings.md` Rejected |
| "Edge scores too high/low for [role type]" | Differentiator calibration off | `differentiators.md` |
| "Requirements scores feel wrong for [role type]" | Target signals or scoring brief | `sources.md` |
| "[Company] isn't appearing but should be" | Missing from priority companies or ATS table | `sources.md` |
| "Comp band is off — wrong roles scoring well on Sustain" | Comp band wrong | `sources.md` Scoring Brief |
| "I want to always see [specific role]" | One-off injection | `learnings.md` Injected |

---

## Step 4 — Propose changes one at a time

For each identified change, show before/after and ask for confirmation before
moving on. Use this format:

```
Proposed change to [file]:
[Plain-English description of what changes]

Before: [current value, or "nothing matching"]
After:  [new value]

Queue this change? (yes / no / tweak it)
```

Keep a running list of queued changes in your working context. Do not write to
any file until Step 5.

If the user says "tweak it", ask what they'd prefer and re-propose before queuing.

---

## Step 5 — Write all queued changes in one pass

Once the user says "that's everything" (or the natural end of signal collection),
summarise the queue:

> "Ready to write [N] changes:
> - sources.md: add 'data infrastructure' to Avoid
> - learnings.md: add Stripe rejection pattern
> Writing now..."

Write all queued changes to their target files. Show a brief confirmation line
per file written.

---

## Step 6 — Close with summary

What changed, which files were updated, and what should be different in the next
feed:

> "Next feed: Stripe won't surface. Roles with 'data infrastructure' in title or
> JD will be filtered before scoring. Edge scoring for fintech-at-scale roles
> unchanged."

---

## What /calibrate can change

- `learnings.md` — rejected patterns, injected roles
- `sources.md` — avoid section, target signals, priority companies, comp band
- `differentiators.md` — edge scoring notes, key differentiator bullets

## What it cannot change without explicit user request

- `feed.md` (the scoring rubric and thresholds) — structural change, risks
  breaking consistency across all scoring. If the user pushes here, flag it and
  ask explicitly: "Changing the scoring rubric is a bigger move — are you sure
  you want to adjust the thresholds, or is there a config file change that would
  fix this instead?"

---

## Rules

- Never write to a file until the user has confirmed the specific change.
- Never batch proposals — show one at a time.
- Do batch writes — all confirmed changes go in a single pass at the end.
- If the feed is less than 2 runs old, note that calibration signal is thin:
  "This is only run [N] — some patterns may not be stable yet. Worth noting these
  and seeing if they repeat."
- British spellings throughout.
