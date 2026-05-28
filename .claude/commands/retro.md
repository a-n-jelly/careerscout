# /retro — Pipeline Retro Protocol

Run every 2-3 weeks, or when 3+ rejections cluster. Takes 5-10 minutes. Covers staleness, rejection patterns, and pipeline health in one pass.

---

## Sequence

Run these four sections in order. Each ends with a single recommended action — not a list.

---

### 1. Staleness Sweep

Read `context/state.md`. Flag every application at **Applied** stage where today's date is past the `Follow-Up By` date.

For each stale application, determine:

- **Follow up**: recruiter name or LinkedIn contact exists in the record → draft a one-line follow-up message and ask if you want to send it
- **Close**: no contact exists, 6+ weeks since applied → recommend moving to "Presumed Closed" and archiving

Output format:

```
## Staleness Sweep

**Follow up:**
- [Company] — [Role]: applied [date], [X] days since. Recruiter: [name]. Suggest follow-up.

**Presume closed:**
- [Company] — [Role]: applied [date], [X] days since, no contact. Recommend archiving.

**Still within window:**
- [Company] — [Role]: applied [date], follow-up window opens [date].
```

If nothing is stale: "All applications within follow-up window."

**Recommended action**: one specific follow-up to send, or one record to archive.

---

### 2. Rejection Cluster Analysis

Pull all rejections since the last retro (or all-time if no prior retro). For each, note:

- Role type (B2C / B2B / startup / enterprise / AI-heavy / fintech / other)
- What you led with in the summary (AI builder / B2B ownership / HSBC scale / other)
- Your fit verdict at time of application
- Stage reached (application / screen / loop)

Then compare against any screens or callbacks in the same period.

Look for patterns:
- Are rejections clustering by role type, company size, or angle?
- Are fit verdicts calibrated? (Investable Stretch converting to screens, or not?)
- Is there one framing that appears in callbacks but not rejections?

If fewer than 3 rejections: skip the pattern analysis. Note the sample is too small.

Output format:

```
## Rejection Analysis

**Rejections since [date]:** [N]
- [Company]: [role type], [angle], [fit verdict], [stage reached]
...

**Screens / callbacks:** [N]
- [Company]: [what was different]

**Pattern observed:** [one honest sentence, or "sample too small to pattern-match"]
```

---

### 3. Hypothesis Log

Based on the pattern (if any), output 1-2 testable hypotheses. Be specific — a hypothesis that can't be tested in the next 3-4 applications isn't useful.

Format each hypothesis as:

```
**Hypothesis:** [specific claim about what's working or not]
**Test:** Next [N] applications of [type], try [specific change]
**Status:** [UNTESTED]
```

Append to `feed-agent/learnings.md` under a `## Resume & Positioning` section (create if it doesn't exist). Tag as `[UNTESTED]`. When a test produces a screen, update to `[SUPPORTED]`. When it doesn't convert after N tries, update to `[REFUTED]` and note what you'd revise.

If no clear pattern: write one hypothesis based on the strongest single signal, and flag the uncertainty explicitly.

---

### 4. Pipeline Summary

Output a clean view of what's actually live:

```
## Pipeline Health

**Active (worth tracking):**
- [Company] — [Role]: [stage], [next action]

**Stale (no response, within window):**
- [Company] — [Role]: [days since applied]

**Presumed closed (recommend archiving):**
- [Company] — [Role]: [days since applied]

**Pre-apply (still being worked):**
- [Company] — [Role]: [what's blocking]
```

**Recommended action**: the single highest-leverage move across the whole pipeline right now — not a prioritised list, just one thing.

---

## State Update

After running `/retro`, add a session log entry to `context/state.md`:

```
| [date] | Retro run. [N] stale, [N] rejections reviewed. Hypotheses: [one-line summary]. |
```

---

## When to Run

- Every 2-3 weeks on a regular cadence
- When 3+ rejections land in quick succession
- Before starting a new batch of applications (to check if positioning should shift)
- When the pipeline feels stale and it's unclear what to do next
