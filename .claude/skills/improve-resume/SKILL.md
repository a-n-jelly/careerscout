---
name: improve-resume
description: >-
  Review and strengthen the master resume. Use when the user says /improve-resume,
  wants to improve their base resume, asks if their resume is strong, or wants
  bullets tightened, the summary sharpened, or weak spots flagged. This works on
  the master resume (context/resume.md) — not a tailored version.
---

# /improve-resume — Resume Review & Strengthening

> ⚠️ **Untested** — this skill has not been validated in real sessions. Use with caution and run `/calibrate` or give feedback if the output feels off.

Reviews the master resume critically and suggests concrete improvements. Output is specific and actionable — not generic advice.

---

## Minimum Data Check

Requires `context/resume.md`. Without it: "Paste your resume and I'll save it to `context/resume.md` before reviewing."

---

## Sequence

### 1. Read context

Read `context/resume.md` and `context/profile.md` (if it exists). The profile gives you off-resume context that might explain or inform what's on the resume.

### 2. Review each section

Work through the resume systematically. For each section assess:

**Summary / Headline**
- Is it specific or generic? Generic = could describe anyone. Specific = only this person.
- Does it lead with the strongest signal, or bury it?
- Does it tell you what kind of roles this person is targeting?

**Each role's bullets**

Flag each bullet as one of:
- ✓ **Strong** — specific, shows ownership, has impact or scale
- ~ **Improvable** — good bones but vague, missing a metric, or underselling
- ✗ **Weak** — generic ("responsible for", "helped with"), no impact, could be anyone

For every ~ or ✗, draft a specific improvement. Don't rewrite for the sake of it — only suggest changes where the improvement is meaningful.

**Structure & ordering**
- Are the most impressive roles and bullets leading?
- Is anything buried that should be prominent?
- Are any sections missing (e.g., no summary, missing key skills)?

**Overall**
- What's the strongest signal in this resume? Is it visible at a glance?
- What would a recruiter flag in the first 10 seconds?

### 3. Form your own view first

Do not ask clarifying questions before producing the review. Read what's there, make judgements, flag what you don't have enough context to assess. Ask targeted questions only for specific bullets where the context would meaningfully change the rewrite.

---

## Output Schema

```markdown
## Resume Review

### What's working
[2-3 sentences on the strongest signals — what lands, what differentiates]

### Summary
[✓ Strong / ~ Improvable / ✗ Weak]
→ [Suggested rewrite if improvable/weak]
Why: [one sentence]

### Bullets by role

**[Company] — [Role]**

| Bullet | Status | Suggested rewrite |
|--------|--------|-------------------|
| [first few words...] | ✓ / ~ / ✗ | [rewrite, or "leave as is"] |

[repeat per role]

### Structure
[Any ordering or structural changes worth making]

### Biggest gaps
[What's missing or underselling that a recruiter would notice — be direct]

### Questions
[Any bullets you couldn't assess without more context — one targeted question each]
```

---

## After the review

Use the AskUserQuestion tool:
- Question: "Want to go through these changes one by one, or pick the ones you want to apply?"
- Options: **Go through all of them** / **I'll pick which ones**

Work through approvals conversationally. Once the user has approved a set of changes, ask:

- Question: "Ready to update your master resume with the approved changes?"
- Options: **Yes, update resume.md** / **No, I'll update it myself**

If yes: apply all approved changes to `context/resume.md` and confirm: "Master resume updated."
If no: summarise the approved changes clearly so the user can apply them manually.
