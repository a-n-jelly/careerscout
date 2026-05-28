# /update — Log an Event Protocol

Use when something happens in the pipeline: interview scheduled, interview completed, heard back, offer received, rejected, withdrawn. Updates `context/state.md` and prescribes the right next action.

---

## Trigger Phrases (mode detection)

- "interview scheduled" / "got a call booked" → log it, set next action, suggest switching to the `interview-coach` agent to prep
- "just finished an interview" / "had my screen today" → log it, capture notes, suggest `/followup`
- "heard back" / "got rejected" / "no longer moving forward" → log rejection, archive if final, suggest next steps
- "got an offer" / "they came back with..." → log offer details, suggest `/negotiate`
- "accepted" / "turning it down" / "withdrawing" → log outcome, archive record

---

## On Interview Completed → suggest `/followup`

After logging a completed interview, always prompt:

> "Want me to draft a follow-up email? It's worth sending within 24 hours."

If yes, run `/followup` for that application.

---

## On Offer Received → suggest `/negotiate`

After logging offer details, always prompt:

> "Want to work through how to respond to this offer? I can help you think through the negotiation."

If yes, run `/negotiate` for that application.

---

## Execution

1. Parse the event from freeform input — don't require structured fields
2. Update the application record in `context/state.md`:
   - Stage and Status
   - Next Action + Next Action Date
   - Timestamped note
   - Comp fields if offer details are given
3. If stage changes to Rejected or Accepted/Withdrawn, move to Archived Applications
4. Confirm what changed and prescribe the next action
5. Trigger `/followup` or `/negotiate` as appropriate (see above)

---

## Output Format

```
Updated. [Company + role] is now at [stage].
[One sentence on what was logged]
[Prescribed next action with reason]
```

Example:
```
Updated. SoFi Borrow is now at Interview Loop — HM screen logged for Thursday.
Next: send a follow-up email within 24 hours. Want me to draft one?
```
