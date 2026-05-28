# /feed reject — Log a Feed Rejection

Logs a role from the current feed as rejected and extracts the disqualifying signal so future runs skip similar roles automatically.

---

## Usage

```
/feed reject [company] [role]
/feed reject [company]         — if role is unambiguous
```

---

## Protocol

### Step 1 — Identify the role

Find the role in `feed/feed.md`. If the match is ambiguous, show the options and ask which one.

### Step 2 — Ask why

Ask one question: "What's wrong with this one?"

Accept any answer — domain mismatch, level, company type, location, specific requirement gap, gut feel. Don't ask follow-ups unless the answer is so vague it can't be turned into a signal (e.g. "just don't like it").

### Step 3 — Extract the signal

From the answer, infer the reusable pattern. Examples:

| User says | Signal tag |
|-----------|-----------|
| "Too infrastructure-focused" | `domain:platform-infra` |
| "Fraud/risk isn't where I'm heading" | `domain:fraud-risk` |
| "Company is too enterprise" | `type:enterprise` |
| "This is a growth role really" | `type:growth-pm` |
| "Level is too senior" | `level:above-target` |
| "Wrong location" | `location:mismatch` |
| "Requires ML depth I don't have" | `req:ml-depth` |

### Step 4 — Route to the right file

Based on the signal tag, write to the appropriate file:

| Signal type | Route to | Action |
|-------------|----------|--------|
| `req:*` (skills gap) | `context/differentiators.md` | Append to `## Hard gaps` section |
| `domain:*` or `type:*` | `context/sources.md` | Append to `## Avoid` section |
| `company:*` | `feed-agent/learnings.md` | Append to `## Rejected` section |
| `level:above-target` | No write needed | Already handled by Stretch section |
| `location:mismatch` | No write needed | Location filtering already active |

Always append to `feed-agent/learnings.md` as a record regardless of where
else the signal routes:

```
- [YYYY-MM-DD] Company — Role Title — [user's reason] | signal:[tag] | routed:[file]
```

Example:
```
- 2026-05-27 SoFi — Principal PM, Fraud Risk & ML Platform — fraud/risk domain not target | signal:domain:fraud-risk | routed:sources.md
```

### Step 5 — Confirm

State what was written and where:
"Logged. [Signal] added to [file] — future runs will filter roles matching this pattern."

Do not re-score or re-rank the current feed. The change takes effect on the next fetch.py run.

---

## Rules

- One rejection per command run. If user wants to reject multiple, they run it again.
- If the signal would filter out something broad (e.g. `company:sofi`), flag it before logging: "This would filter all SoFi roles — is that what you want?"
- Never log a signal that conflicts with the Priority Companies list without confirming first.
