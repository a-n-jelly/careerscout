# /feed-review — Post-Run Feedback Session

Walk through the recommended roles from today's feed, capture reactions, and log any rejections to learnings.md so future runs filter them automatically.

Run this after reviewing feed/daily-feed-output.md. Takes 5–10 minutes.

---

## Protocol

### Step 1 — Load the feed

Read `feed/daily-feed-output.md`. Extract the recommended list only. If there's nothing recommended, say: "No recommended roles to review — nothing to log."

### Step 2 — Walk through each role

Present each recommended role one at a time in this format:

```
[N of M] Company — Role Title [ABOVE LEVEL?] [TARGET?]
Score: Match N / Requirements N / Edge N / Sustain N = Total/12
Why: [the "Why this is yours" line from the feed]
Link: [URL]

Key requirements:
- [req 1]
- [req 2]
- [req 3]
- [req 4]
- [req 5]
```

Pull the link and key requirements directly from the feed output — they're already in the `<details>` block per role.

Ask: **"Worth pursuing? yes / no / maybe"**

- **yes / maybe**: move on, no logging
- **no**: ask one follow-up — "What's the mismatch?" — then log it (see Step 3)

Do not ask more than one follow-up question per rejection.

### Step 3 — Log rejections

For each "no", extract the signal from the user's answer and append to `feed-agent/learnings.md`:

```
- [YYYY-MM-DD] Company — Role Title — [reason] | signal:[tag]
```

Signal tags to use:

| Pattern | Tag |
|---------|-----|
| Wrong domain (fraud, risk, ML, infra, platform) | `domain:[descriptor]` |
| Above level, not worth pursuing | `level:above-target` |
| Company type wrong (enterprise, B2B, etc.) | `type:[descriptor]` |
| Specific missing requirement | `req:[descriptor]` |
| Location despite data saying OK | `location:mismatch` |
| Growth/acquisition focus | `type:growth-pm` |

If the signal would filter a broad category (e.g. all SoFi roles), flag it: "This pattern would filter all [Company] roles in future — is that right?"

### Step 4 — Summary

After all roles reviewed, output:

```
Reviewed [N] roles. Logged [N] rejections.

Logged signals:
- [signal tag]: [company — role]
- ...

These patterns will pre-filter from the next fetch run.
```

---

## Rules

- Move at pace — this isn't `/assess`. One question per role, no deep dives.
- If the user says "I'll think about it" or is unsure, treat as maybe and move on.
- Never update `context/sources.md` scoring criteria during a review session — that's a separate conversation. Review is for logging, not redesigning.
- If the user wants to go deeper on a role, say: "Run `/assess` on that one after we finish the review."
