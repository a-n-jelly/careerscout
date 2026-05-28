# /notes — Quick Capture Protocol

Lightweight capture for raw input that doesn't fit a structured workflow. The goal is to file information to the right place without requiring you to structure anything.

---

## When to Use

- Raw recruiter feedback after a call
- Something remembered after a previous session
- Context about a company or role that's worth keeping
- A question a recruiter asked that should inform prep
- Anything that starts with "I should remember that..."

---

## Sequence

1. Accept whatever is pasted — don't require a specific format.
2. Identify what type of information it is and where it belongs:
   - Recruiter feedback on a specific application → `context/state.md` under that application
   - New cover letter point or example → `context/bank.md`
   - General career context → `context/profile.md`
3. Confirm what was captured and where it was filed: "Captured. Filed under [application name] in state.md — I'll use it when we work on that cover letter."
4. If something in the capture suggests a next action, name it: "This feedback suggests the [concern] is real. Worth running `/concerns` for this role if you haven't."

---

## Output

Brief confirmation only — no schema. Match the weight of the output to the weight of the input. This is a capture command, not an analysis command.

**No forced next step** — only suggest one if the capture clearly implies one.
