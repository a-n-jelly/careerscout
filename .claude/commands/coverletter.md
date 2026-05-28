# /coverletter — Cover Letter Writing Protocol

---

## Minimum Data Check

Requires a JD (pasted or in state). Without it: "Paste the JD and I'll write the letter."

If `/assess` hasn't been run for this role yet, run a quick internal assessment first (don't output it) to identify the 2-3 themes to lead with. Say: "I haven't assessed this role yet — I'll do a quick read of the JD before writing."

---

## Sequence

1. **Identify the 3 themes** that best bridge the JD's priorities with your strongest evidence. These become the bold headers. Draw from:
   - `/assess` output if it exists for this role
   - `context/bank.md` → Ready-to-Use Points
   - `context/bank.md` → Gaps to Handle Carefully (to know what to avoid)

2. **Check the bank for coverage gaps.** For each theme, do the points in `bank.md` cover it, or is there a hole? If there's a hole, ask one clarifying question before writing — not a list of questions, one at a time. Save every answer to `bank.md` immediately.

3. **Draft the letter** following the style in `context/bank.md`:
   - Opening: role name, team, relocation context (if relevant), tie to company mission in their own language
   - Body: 2-4 bold headers as prose paragraphs (3-5 sentences each), not bullets
   - Closing: one sentence tied to the specific team or product
   - Sign-off: `Kind Regards, / [your name]` — pull from `context/bank.md` if set

4. **Independent quality check before delivering.** Before outputting, assess: Does this read like a Staff PM or like someone justifying their application? Is every paragraph earning its place, or is anything filler? Cut anything that doesn't directly serve the letter's argument.

---

## Style Constraints (from bank.md examples)

- Tone: warm but assured — you're choosing them too, not auditioning
- British English throughout
- No "leveraging", "robust", "meticulous", "synergy", "dynamic"
- No three-adjective constructions
- Short punchy sentences for impact alongside longer ones — vary the rhythm
- Every example leads with context, follows with impact
- No abrupt summary endings

---

## Output Schema

```markdown
## Cover Letter: [Company] — [Role]

---

[Letter text — formatted exactly as it would be sent]

---

## Draft Notes
- Themes used: [list the 3 headers and which bank points each draws from]
- Concerns addressed: [how the top concern from /concerns is handled, if applicable]
- What's missing: [anything that would strengthen this if you can provide more context]
```

---

## Saving

After producing the letter, use the AskUserQuestion tool:
- Question: "Want me to save this to `cover-letters/[company-role].md`? You can also copy it directly if you're pasting into an application form."
- Options: **Yes, save it** / **No, I'll copy it**

If yes: save to `cover-letters/[company-role].md` and update the application record in `context/state.md`:
- **Cover Letter**: cover-letters/[company-role].md
- Add a timestamped note: `[date]: Cover letter drafted.`

If no: update state.md with a timestamped note only: `[date]: Cover letter drafted (not saved to file).`
