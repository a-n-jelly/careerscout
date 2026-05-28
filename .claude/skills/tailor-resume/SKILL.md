---
name: tailor-resume
description: >-
  Tailor a resume to a specific job description. Use when the user says /tailor,
  wants to adapt their resume for a role, or asks which bullets or summary to
  change for a specific application. Always invoke my-voice before drafting any
  output.
---

# /tailor — Resume Tailoring Protocol

Tailors the full resume to a specific JD. Output is a set of recommended changes, not a rewrite of the whole document. Always invoke the my-voice skill before producing any written output.

---

## Minimum Data Check

Requires a JD. Without it: "Paste the JD and I'll tailor the resume to it."

---

## Core rules

**Do not mirror JD language.** The goal is resonance, not reflection. Hiring managers notice copy-paste framing immediately. Improve what's already there: sharpen weak bullets, reframe for the right audience, make implicit strengths explicit. Every change should sound like something Anjali would actually say, not like the JD fed back.

**Write from her words, not from synthesis.** When drafting bullets, start from what she actually said, not from a polished analytical version of it. If a bullet sounds like a post-mortem or a case study, that's a signal to stop and ask what actually happened. Plain language with a specific insight is stronger than dressed-up jargon. When she pushes back on phrasing, ask her to describe it herself before offering another rewrite.

**Don't rewrite bullets that are already strong.** Before suggesting a change, ask: is this actually weak, or am I just looking for something to do? If a bullet is already doing the job, say so explicitly and move on. Rewriting for the sake of it introduces fabricated framing and erodes trust in the output.

---

## Sequence

1. **Read the JD and identify what it actually cares about.** Look past boilerplate: what does the language, ordering, and emphasis reveal about what they'll hire on?

2. **Read `context/resume.md` and `context/profile.md`.** Cross-reference against the JD. Redraft from these files directly. No bullet bank.

3. **Assess the summary first.** Does it lead with the right angle for this JD? Draft a tailored version if not.

4. **Identify which bullets need changing.** Don't rewrite everything — focus on:
   - Bullets most relevant to the JD that are underselling
   - Bullets using the wrong framing for this role type (e.g., B2B language for a consumer role)
   - Bullets missing entirely for a JD priority Anjali can actually speak to

5. **Form your own view of what's weak** before asking for context. Ask one targeted question only if reframing genuinely requires information you don't have.

6. **Show before/after for each change** with a one-line explanation of what changed and why.

7. **Get approval before saving anything** to a file. Do not auto-save bullets or summaries.

---

## Output Schema

```markdown
## Resume Tailoring: [Company] — [Role]

### Summary
→ [new version]
Why: [one sentence — include original only if the contrast materially helps]

### Bullet Changes

**[Role/Company section]**

→ [Rewrite]
Why: [one sentence — include original only if the contrast materially helps]

[repeat per bullet]

### Drop
[Bullets to remove, with one-line reason]

### Leave Unchanged
[Bullet text only — no explanation needed]

### Needs More Information
[Any rewrites blocked on context you don't have, with the specific question]
```

**Recommended next**: `/coverletter` — use the tailored framing as the basis for the letter.

---

## State Update

Add a timestamped note to the application record in `context/state.md`: `[date]: Resume tailored. Resume Used: resumes/[filename].md`
