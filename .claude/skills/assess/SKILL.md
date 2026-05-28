---
name: assess
description: >
  Fit assessment protocol for job applications. Use this skill whenever a job description is pasted,
  a role is being evaluated, or the user asks whether a role is worth applying to. Also trigger when
  the user asks "is this a good fit?", "what do you think of this role?", "should I apply?", or shares
  a JD without an explicit command. Produces a structured fit verdict, dimension scores, recruiter
  concerns ranked by severity, and a cover letter angle.
---

# /assess — Fit Assessment Protocol

## Minimum Data Check

Requires a job description. If none is present, say: "Paste the job description and I'll run the assessment."

---

## Sequence

1. **Read the JD independently.** Extract: required skills, seniority signals, team context, and any language that reveals what they actually care about vs. what's boilerplate.
2. **Check `context/profile.md`** for a `## Mnookin Doc` section. If present, use it to assess Mnookin fit (see below). If absent, skip that section of the output.
3. **Form your own assessment before asking anything.** Score fit across four dimensions (see below). Don't ask how the user feels about the role first — their enthusiasm shouldn't colour the assessment.
4. **Then ask one question if something is ambiguous** that would materially change the verdict. One question only.
5. **Output the assessment.**

---

## Fit Dimensions

Score each as **Strong / Moderate / Weak** with a one-line rationale:

- **Requirement Coverage**: Does their experience hit the stated requirements? Note frameable gaps (can be addressed with narrative) vs. structural gaps (genuinely missing).
- **Seniority Alignment**: Does the level match? Watch for roles that want IC execution *and* strategic ownership — that's a scope question worth flagging.
- **Domain Relevance**: How transferable is their background? Assess the distance between what they've done and what the role requires.
- **Differentiation Potential**: Where do they have a genuine edge over a strong candidate pool? This shapes the cover letter angle.

### Domain gap calibration

Before calling a domain gap structural, check two things:

1. **Is it actually in the JD?** Distinguish between stated requirements and implied domain knowledge. If the JD lists skills and experiences without naming a specific domain, the gap is frameable — not structural. Only call it structural if the JD explicitly requires prior domain experience (e.g. "5+ years in adtech", "experience with DSPs required").

2. **Is the underlying problem transferable?** Map the core competency the role needs to what the candidate has actually done. The domain label may differ; the product challenge may not.

**On quantitative backgrounds:** A strong quantitative degree (Economics, Statistics, Mathematics) is a legitimate proxy for math/stats. Don't treat it as a gap unless the JD specifically requires a STEM or CS degree.

**On referrals:** A referral upgrades the verdict by at least one tier — it means the resume gets seen by a human, and someone with inside context has already judged the fit worth pursuing. Factor this in before outputting the verdict.

**Verdict**: Strong Fit / Investable Stretch / Long-Shot Stretch / Weak Fit

If Long-Shot Stretch or Weak Fit: skip the full schema. Output a short paragraph — the verdict, the core reason, and whether there's any angle worth pursuing. Nothing else.

---

## Recruiter Concerns

List concerns ranked by severity. For each:

- **Dealbreaker**: Could single-handedly end the candidacy if unaddressed
- **Significant**: Will come up, needs a strong counter
- **Minor**: Might come up as a probe, unlikely to be decisive

For each Significant+ concern, provide:
- How it surfaces as a direct question
- How it surfaces as a subtle probe
- The one-sentence counter

---

## Output Schema

```markdown
## Fit Assessment: [Company] — [Role]

### Verdict: [Strong Fit / Investable Stretch / Long-Shot Stretch / Weak Fit]

### Dimension Scores
- Requirement Coverage: [Strong / Moderate / Weak] — [rationale]
- Seniority Alignment: [Strong / Moderate / Weak] — [rationale]
- Domain Relevance: [Strong / Moderate / Weak] — [rationale]
- Differentiation Potential: [Strong / Moderate / Weak] — [rationale]

### What Lands
[2-3 specific things from the user's background that directly match what they're asking for]

### Recruiter Concerns

**Dealbreakers**
[list if any — or "None identified"]

**Significant**
1. Concern:
   Direct question: "..."
   Subtle probe: "..."
   Counter: [one sentence]

**Minor**
1. [concern + one-line counter]

### Mnookin Fit
[Only include if a ## Mnookin Doc section exists in context/profile.md. See Mnookin Fit section below for how to score this.]

### Cover Letter Angle
[The 2-3 themes to lead with, given this specific JD. Not generic — drawn from where the user's profile overlaps with what they actually care about.]
```

**Recommended next**: `/coverletter` — build the letter around the angle above. **Alternative**: `/tailor` if the resume needs targeted rewrites first.

---

## Mnookin Fit

If `context/profile.md` contains a `## Mnookin Doc` section, read it before producing the assessment. Use it to evaluate whether this company and role *feel like the right environment* — not whether the candidate meets the requirements (that's covered in the dimensions above).

Look for signals in the JD, company description, and any public information about the company culture that match or conflict with the stated preferences. Signals to check:

- **Company style**: startup scrappiness vs. process-driven vs. autonomous — does it match their stated preference?
- **Team structure**: collaborative vs. independent, cross-functional vs. siloed — any flags?
- **Working environment**: pace, ownership model, how decisions are made
- **Culture markers**: mission-driven, commercial-first, technical culture, design-led — do they align with what the user values?

Output as one of three ratings with a brief rationale:

- **Mnookin friendly** — the signals available suggest this environment matches their preferences
- **Mixed signals** — some things fit, some don't — flag specifically what aligns and what doesn't
- **Likely not Mnookin friendly** — clear mismatches with stated preferences — name them

Note: this is a signal based on limited public information, not a definitive read. The user should verify in the interview process.

If no Mnookin Doc is present, omit this section entirely. Do not mention it.

---

## State Update

After assessment, add to `context/state.md`:
```
| [Company] | [Role] | Assessed — [verdict] | [date] |
```

---

## Gap Write-Back

After assessment, check the Requirement Coverage dimension and Recruiter
Concerns for structural gaps — things identified as genuinely missing, not
frameable.

If any structural gaps are found that don't already exist in the
`## Hard gaps` section of `context/differentiators.md`, surface them and
ask before writing:

> "I identified [N] structural gap(s) not in your hard gaps list:
> - [gap 1]
> - [gap 2]
> Should I add any of these? (confirm each)"

Only write confirmed gaps. Frameable gaps (addressable with narrative)
do not belong here — they stay in the assessment output only.

---

## Self-Update on Feedback

When the user pushes back on a verdict, challenges a concern, or provides context that changes the assessment, do two things:

1. Revise the output based on what they said.
2. If the correction reveals a reusable principle — something that would apply to future assessments, not just this one — append it to the Calibration Log below. Keep each entry tight: the rule, why it exists, and when to apply it.

Don't log one-off context (e.g. "this specific company prefers X"). Only log patterns that generalise.

---

## Calibration Log

Entries added during sessions when assessments were corrected or refined.

- **Don't overweight implied domain gaps.** If the JD doesn't explicitly require domain experience, a domain gap is frameable, not structural. Check whether the underlying product problem is transferable before calling it a gap. **Why:** Easy to over-call a Long-Shot when the JD requires transferable skills (e.g. data-driven PM) rather than specific domain experience. **Apply when:** Any role outside the candidate's primary domain — check the JD requirements literally before penalising for domain distance.
