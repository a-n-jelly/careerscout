# /track — Application Tracker Protocol

Manages the full lifecycle of applications: adding new ones, updating status and details, and viewing the pipeline. This is the source of truth for where every application stands.

---

## Sub-commands

- `/track add` — Add a new application
- `/track update [company]` — Update an existing application's details or status
- `/track status` — View the full pipeline summary
- `/track [company]` — View the full record for one application

If no sub-command is given, default to `/track status`.

---

## Stages (use these exactly, in order)

| Stage | Meaning |
|-------|---------|
| **Researching** | Evaluating whether to apply — no application submitted |
| **Drafting** | Cover letter or bullets in progress |
| **Applied** | Submitted, awaiting response |
| **Recruiter Screen** | First call scheduled or completed |
| **Interview Loop** | Active interview rounds in progress |
| **Offer** | Offer received, evaluating or negotiating |
| **Accepted** | Offer accepted |
| **Withdrawn** | You withdrew |
| **Rejected** | No longer active — company passed |
| **Paused** | On hold — JD closed, role frozen, timing issue |

---

## `/track add` — New Application

Ask for details in a single pass — not one question at a time for a data entry task. Present as a form:

```
Adding new application. Fill in what you know — leave anything blank and we'll add it later:

- Company:
- Role Title:
- Team / Product Area:
- Salary Range (from JD):
- Location / Remote:
- Recruiter name + contact:
- Hiring Manager (if known):
- Date Applied (or "not yet"):
- Source (where you found it):
- Any notes:
```

After receiving the details, create the application record in `context/state.md` using the full record template below, and add a row to the Pipeline Summary table. Set Cover Letter to `cover-letters/[company-role].md` (even if the file doesn't exist yet) and Resume Used to the relevant file in `resumes/`.

Then ask: "Want me to run `/assess` on this role now, or are you just tracking it for now?"

---

## `/track update [company]` — Update an Application

Accept freeform input — no need to match field names. Parse what you get and update the right fields.

**Examples of valid update inputs:**
- "Got a recruiter call booked for Monday" → Stage: Recruiter Screen, Next Action: Recruiter call, Next Action Date: Monday
- "They came back with $180k base, $40k bonus, 25k RSUs" → Salary Range (Offer), add to Notes
- "Rejected after final round — no feedback given" → Status: Rejected, Stage: Rejected, add to Notes
- "Hiring manager is Sarah Chen, found her on LinkedIn" → Hiring Manager: Sarah Chen
- "Moving to Interview Loop — 3 rounds, first one is a HM screen next Thursday" → Stage: Interview Loop, Interview Rounds: 3 rounds (1: HM screen [date]), Next Action Date: Thursday

After updating, confirm what changed: "Updated. SoFi Borrow is now at Interview Loop stage — HM screen Thursday. Want to run `/concerns` to prep for that?"

**If the company name is ambiguous** (e.g., two SoFi roles), ask which one before updating.

---

## `/track status` — Pipeline View

Output the Pipeline Summary table plus a brief "What needs attention" section based on the data.

```markdown
## Application Pipeline

| Company | Role | Stage | Next Action | Date |
|---------|------|-------|-------------|------|
| [company] | [role] | [stage] | [next action] | [date] |
...

## What Needs Attention
- [Any application with a next action date in the past — flag as overdue]
- [Any application at Interview Loop with no `/concerns` run — suggest it]
- [Any application at Offer with no comp notes — suggest `/track update`]
- [Any application stuck at Applied for 3+ weeks with no update — flag]
```

Keep "What needs attention" to the 2-3 most actionable items. Don't list everything — prioritise.

---

## `/track [company]` — Single Application View

Output the full record for that application. If multiple applications exist for the same company, ask which one.

---

## Application Record Template

Use this structure for every record in `context/state.md`:

```markdown
### [Company] — [Role Title]

- **Status**: [Active / Submitted / Rejected / Offer / Accepted / Withdrawn / Paused]
- **Stage**: [from stage list above]
- **Date Applied**: —
- **Source**: —
- **Role Title**: —
- **Team / Product Area**: —
- **Salary Range (JD)**: —
- **Salary Range (Offer)**: —
- **Bonus**: —
- **Equity**: —
- **Comp Target**: —
- **Location / Remote**: —
- **Recruiter**: —
- **Hiring Manager**: —
- **Interview Rounds**: —
- **Next Action**: —
- **Next Action Date**: —
- **Follow-Up By**: [Date Applied + 14 days — auto-set on apply]
- **Cover Letter**: cover-letters/[company-role].md
- **Resume Used**: resumes/resume-master.pdf
- **Fit Verdict**: [from /assess, or —]
- **Top Concern**: [from /concerns, or —]

**Notes**:
- [Timestamped notes, newest at top]
```

---

## State Update Rules

- Always update the Pipeline Summary table to match the record
- Timestamp all notes entries: `[date]: [note]`
- When stage changes to Rejected or Accepted, move the record to an **Archived Applications** section at the bottom of state.md (keeps the active pipeline clean)
- Never delete records — archive them
