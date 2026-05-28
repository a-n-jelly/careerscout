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

**Do not mirror JD language.** The goal is resonance, not reflection. Hiring managers notice copy-paste framing immediately. Improve what's already there: sharpen weak bullets, reframe for the right audience, make implicit strengths explicit. Every change should sound like something the user would actually say, not like the JD fed back.

**Write from their words, not from synthesis.** When drafting bullets, start from what the user actually said, not from a polished analytical version of it. If a bullet sounds like a post-mortem or a case study, that's a signal to stop and ask what actually happened. Plain language with a specific insight is stronger than dressed-up jargon. When they push back on phrasing, ask them to describe it themselves before offering another rewrite.

**Don't rewrite bullets that are already strong.** Before suggesting a change, ask: is this actually weak, or am I just looking for something to do? If a bullet is already doing the job, say so explicitly and move on. Rewriting for the sake of it introduces fabricated framing and erodes trust in the output.

**Rephrasing alone is not a change worth making.** If the only difference between the original and the suggested version is word choice or sentence structure — and the meaning, emphasis, and impact are the same — do not suggest it. A change must add something: a sharper angle, a clearer outcome, a more relevant framing for this specific role. If it doesn't, leave the original.

---

## Tailoring preferences

Read `context/bank.md` before starting. If it contains a `## Tailoring preferences` section with filled-in values, follow those instructions — they override defaults where they conflict.

**If the section is empty or missing**, this is the user's first tailor session. Use the AskUserQuestion tool to set preferences before proceeding:

- Question: "Before we start — a couple of quick questions so I tailor the right way for you."
- Ask in a single tool call:
  - **How much do you want to change?** Options: Minimal — only change bullets that are clearly wrong for this role / Moderate — suggest meaningful reframes where they'd help / Aggressive — tailor heavily to the JD
  - **Rephrasing:** Options: Skip it — if it's just rewording, leave the original / Allow it — suggest if it improves clarity or flow
  - **JD language:** Options: Never parrot it — keep my voice throughout / OK for key terms — match their language where it matters

Save the answers to the `## Tailoring preferences` section in `context/bank.md` immediately. Confirm: "Got it — saved your preferences. I'll follow these every time."

---

## Sequence

1. **Read the JD and identify what it actually cares about.** Look past boilerplate: what does the language, ordering, and emphasis reveal about what they'll hire on?

2. **Read `context/resume.md` and `context/profile.md`.** Cross-reference against the JD. Redraft from these files directly. No bullet bank.

3. **Assess the summary first.** Does it lead with the right angle for this JD? Draft a tailored version if not.

4. **Identify which bullets need changing.** Don't rewrite everything — focus on:
   - Bullets most relevant to the JD that are underselling
   - Bullets using the wrong framing for this role type (e.g., B2B language for a consumer role)
   - Bullets missing entirely for a JD priority the user can actually speak to

5. **Form your own view of what's weak** before asking for context. Ask one targeted question only if reframing genuinely requires information you don't have.


6. **Show before/after for each change** with a one-line explanation of what changed and why.

7. **Get approval before saving anything** to a file. Do not auto-save bullets or summaries.

8. **After the user approves the changes**, use the AskUserQuestion tool:
   - Question: "Want me to save the full tailored resume as a markdown file? It's useful as a reference even if you maintain your actual resume in another format (Google Docs, Word, etc.)."
   - Options: **Yes, save it** / **No thanks**

   If yes: compile the full resume by applying all approved changes to `context/resume.md` and save to `resumes/[company-role].md`. Confirm: "Saved to `resumes/[company-role].md`."

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

---

## Learning from the session

After going through bullets with the user, capture what you observed and update `context/bank.md` and `context/profile.md` silently — do not announce unless the inferred rule is ambiguous.

**Watch for:**
- **Accepted rewrites** — what kind of change did they approve? (sharper metric, reframed angle, dropped jargon). Reinforce in Tailoring preferences if there's a pattern.
- **Pushed-back rewrites** — what did they reject and why? Common signals: "too formal", "that's not how I'd say it", "don't change this", "you're parroting the JD". Add a rule to Tailoring preferences.
- **Their own rewrites** — if the user rewrites a bullet themselves, treat it as a voice example. Capture the before/after and add a rule to bank.md or my-voice/SKILL.md.
- **Profile context** — if the user explains why a bullet is worded a certain way ("I was actually doing X not Y"), add that context to `context/profile.md` under the relevant role.

Format learned rules as: `- [what to do / avoid] (learned from: tailor session [date])`

---

## State Update

Add a timestamped note to the application record in `context/state.md`: `[date]: Resume tailored. Resume Used: resumes/[company-role].md` (or "Resume Used: external" if the user declined to save).
