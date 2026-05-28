# /voice-setup — Writing Voice Calibration

Builds `skills/my-voice/SKILL.md` from real writing samples rather than self-description.

---

## When to use

Run this once at the start, before using `/coverletter`, `/tailor`, or any other command that produces written output. It takes 5-10 minutes and makes every subsequent output significantly more accurate.

---

## Protocol

### Step 1 — Request samples

Say:

> "Paste 3-5 pieces of writing that sound like you — emails, messages, LinkedIn posts, cover letters, anything you've written that feels right. The more varied the better. I'll read them and draft your voice profile."

Wait. Do not proceed until samples are provided.

### Step 2 — Analyse

Read all samples before drawing any conclusions. Look for:

**Rhythm and structure**
- Typical sentence length — short and punchy, or longer and flowing?
- Do they use fragments? Lists? How often?
- How do they open a piece of writing? How do they close?
- Do they announce structure ("here are three things…") or just move through it?

**Tone**
- Formal or casual? Does it shift by context?
- Warm, dry, direct, cautious, playful?
- How do they handle uncertainty — hedge or commit?
- Do they soften criticism or name it plainly?

**Word choices**
- Any recurring words or phrases that feel like signature moves?
- Any words they conspicuously avoid?
- Do they use jargon, or plain language?

**Humour**
- Is there any? What kind — dry, self-deprecating, ironic?
- Does it show up in professional writing or only casual?

**What's absent**
- No corporate filler? No qualifications? No recap paragraphs?
- Note the omissions — they're as telling as what's there.

### Step 3 — Draft the skill

Fill in `skills/my-voice/SKILL.md` based on the evidence. For each section:
- State the rule clearly
- Annotate it with a brief note citing what in the samples led to it (e.g. *"You closed three out of four emails without a sign-off sentence — just the point and your name."*)

Do not invent rules not evidenced in the samples. If a section has no signal, say so and leave it as a question for the user.

### Step 4 — Review

Show the user the drafted sections in full. Say:

> "Here's what I extracted. Read through it — correct anything that's wrong, add anything I missed, and delete anything that doesn't feel right. Pay particular attention to the examples table at the bottom."

Make any corrections. Then write the final version to `skills/my-voice/SKILL.md`.

### Step 5 — Confirm

Say:

> "Voice profile saved. I'll use this from now on, and update it automatically when you correct my output."
