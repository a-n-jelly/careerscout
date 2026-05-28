# /concerns — Recruiter Concern Anticipation Protocol

Dedicated workflow for pressure-testing your candidacy before writing or submitting. More thorough than the concerns section in `/assess` — this one drills into counter-framings and can flow directly into a practice drill.

---

## Minimum Data Check

Requires either: (a) an active application with a JD in `context/state.md`, or (b) a JD pasted in the current session. If neither exists: "Paste the JD and I'll map the concerns."

---

## Sequence

1. **Pull all data sources** before generating concerns:
   - JD requirements vs. resume gaps
   - `context/bank.md` → "Gaps to Handle Carefully" section
   - Any prior `/assess` output for this role
   - Storybank coverage (do you have a story for each likely concern area?)

2. **Generate concerns independently.** Don't ask what you're worried about first — blind spots are part of what this is for. After generating, ask: "Which of these did you already expect? Anything I missed?"

3. **Rank by severity** (Dealbreaker → Significant → Minor).

4. **Attach counter-framings** for every Significant+ concern:
   - Direct question version
   - Subtle probe version
   - Follow-up challenge (the pushback after your first answer)
   - Best story to deploy (from resume/bank)

5. **Offer a live drill** on the top concern: "Your biggest concern is [X]. Want to practice handling it right now? I'll run the direct question, then the subtle probe, then the follow-up challenge."

---

## Output Schema

```markdown
## Recruiter Concerns: [Company] — [Role]

### Dealbreakers
[If none: "No dealbreakers identified — the gaps here are frameable."]

1. **[Concern]**
   Why it's a dealbreaker: [one sentence]
   Direct question: "[e.g., 'You haven't owned a consumer product — why should we believe you can lead one here?']"
   Counter: [how to answer head-on]
   Subtle probe: "[e.g., 'Tell me about a time you had to learn a new domain quickly']"
   Counter: [how to handle the indirect version]
   Follow-up challenge: "[e.g., 'But isn't that a different scale entirely?']"
   Counter: [how to hold the line after pushback]
   Best story: [story title + why it works here]

### Significant
[list with same structure]

### Minor
1. **[Concern]** — [one-sentence counter]

### What's NOT a Concern
[1-2 things you might be worried about that the JD doesn't actually signal. Saves prep energy.]

### Drill Offer
Your top concern is [X]. Want to practice it now?
- Round 1: Direct question
- Round 2: Subtle probe
- Round 3: Follow-up challenge after your answer
```

**Recommended next**: `/coverletter` — address the top concerns proactively in the letter. **Alternative**: `/tailor` — reframe the resume sections that are triggering these concerns.

---

## State Update

Save top 2 concerns to the relevant application in `context/state.md` so `/coverletter` and `/review` can reference them without re-deriving.
