# /feed add — Inject a Role into the Feed

Manually adds a role to the feed — useful for roles you found yourself that didn't surface via the daily fetch.

---

## Usage

```
/feed add [url]
/feed add             — then paste JD
```

---

## Protocol

### Step 1 — Get the role

If a URL is provided, say: "Paste the job description and I'll score it."
If they paste directly, proceed.

### Step 2 — Score it

Score the role using the same 4-dimension rubric from `/feed`:
- Match / Requirements / Edge / Sustain (0–3 each)
- Apply level detection: check title for Principal/Staff/Director signals → `[ABOVE LEVEL]` tag if present
- Apply avoid list from `context/sources.md`

### Step 3 — Show the score

Output in the same format as feed.md:

```
### [Role Title] — [Company] [ABOVE LEVEL?] [TARGET?]
- **Fit score:** Match N / Requirements N / Edge N / Sustain N = Total/12
- **Why this is yours:** [one sentence]
- **Link:** [url or "pasted — no link"]
- **Location:** [location] · [Remote / Hybrid / On-site]
- **Comp:** [if listed]
```

Ask: "Add this to your feed and learnings? (yes / no)"

### Step 4 — Log if confirmed

If yes, append to `feed-agent/learnings.md` injected section:

```
- [YYYY-MM-DD] Company — Role Title — [why you're adding it]
```

Also append the scored entry to `feed/feed.md` under the Recommended section (or a new `## Manually Added` section if score is below threshold).

### Step 5 — Confirm

Say: "Added. It'll appear in future feeds too until you reject it."

---

## Rules

- Score honestly — don't inflate because the user found it themselves.
- If the role hits the avoid list, say so and ask if they want to override.
- If it's already in `context/state.md` (active application), say so and skip the inject.
